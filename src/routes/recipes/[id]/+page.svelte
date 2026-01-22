<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
	import type { Recipe, ScaledIngredient, CookingTimer, RecipeNutrition, RecipeCost } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import {
		getTimers,
		addTimer,
		startTimer,
		pauseTimer,
		resumeTimer,
		resetTimer,
		removeTimer,
		formatTime,
		requestNotificationPermission
	} from '$lib/stores/timers';
	import { dietaryTagLabels, dietaryTagColors } from '$lib/constants/dietary-tags';

	let recipe: Recipe | null = $state(null);
	let scaledIngredients: ScaledIngredient[] | null = $state(null);
	let nutrition: RecipeNutrition | null = $state(null);
	let cost: RecipeCost | null = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let targetServings = $state(4);

	let newTimerName = $state('');
	let newTimerMinutes = $state(10);
	let newNoteContent = $state('');
	let editingNoteId = $state<number | null>(null);
	let editingNoteContent = $state('');

	const timers = $derived(getTimers());

	$effect(() => {
		if (recipe) {
			targetServings = recipe.servings;
		}
	});

	onMount(async () => {
		requestNotificationPermission();
		try {
			recipe = await api.get<Recipe>(`/recipes/${$page.params.id}`);
			loadNutritionAndCost();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipe';
		} finally {
			loading = false;
		}
	});

	async function loadNutritionAndCost() {
		if (!recipe) return;
		try {
			const [nutritionData, costData] = await Promise.all([
				api.get<RecipeNutrition>(`/recipes/${recipe.id}/nutrition?servings=${targetServings}`),
				api.get<RecipeCost>(`/recipes/${recipe.id}/cost?servings=${targetServings}`)
			]);
			nutrition = nutritionData;
			cost = costData;
		} catch {
			/* ignore - nutrition/cost data is optional */
		}
	}

	async function scaleRecipe() {
		if (!recipe) return;
		try {
			scaledIngredients = await api.get<ScaledIngredient[]>(
				`/recipes/${recipe.id}/scale/${targetServings}`
			);
			loadNutritionAndCost();
		} catch {
			/* ignore */
		}
	}

	async function toggleFavorite() {
		if (!recipe) return;
		try {
			if (recipe.is_favorite) {
				await api.delete(`/favorites/${recipe.id}`);
			} else {
				await api.post(`/favorites/${recipe.id}`);
			}
			recipe.is_favorite = !recipe.is_favorite;
		} catch {
			/* ignore */
		}
	}

	async function deleteRecipe() {
		if (!recipe || !confirm('Delete this recipe?')) return;
		try {
			await api.delete(`/recipes/${recipe.id}`);
			goto('/recipes');
		} catch {
			/* ignore */
		}
	}

	function handleAddTimer() {
		if (!newTimerName.trim() || newTimerMinutes <= 0) return;
		const id = addTimer(newTimerName, newTimerMinutes);
		startTimer(id);
		newTimerName = '';
		newTimerMinutes = 10;
	}

	function quickTimer(minutes: number) {
		const id = addTimer(`${minutes} min timer`, minutes);
		startTimer(id);
	}

	async function handleAddNote() {
		if (!recipe || !newNoteContent.trim()) return;
		try {
			const note = await api.post<{ id: number; content: string; created_at: string; updated_at: string }>(
				`/recipes/${recipe.id}/notes`,
				{ content: newNoteContent }
			);
			recipe.notes = [...recipe.notes, note];
			newNoteContent = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add note';
		}
	}

	async function handleUpdateNote() {
		if (!recipe || editingNoteId === null || !editingNoteContent.trim()) return;
		try {
			const note = await api.put<{ id: number; content: string; created_at: string; updated_at: string }>(
				`/recipes/${recipe.id}/notes/${editingNoteId}`,
				{ content: editingNoteContent }
			);
			recipe.notes = recipe.notes.map((n) => (n.id === editingNoteId ? note : n));
			editingNoteId = null;
			editingNoteContent = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update note';
		}
	}

	async function handleDeleteNote(noteId: number) {
		if (!recipe || !confirm('Delete this note?')) return;
		try {
			await api.delete(`/recipes/${recipe.id}/notes/${noteId}`);
			recipe.notes = recipe.notes.filter((n) => n.id !== noteId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete note';
		}
	}

	function getDifficultyClass(diff: string): string {
		const classes: Record<string, string> = {
			easy: 'diff-easy',
			medium: 'diff-medium',
			hard: 'diff-hard'
		};
		return classes[diff] || '';
	}
</script>

{#if loading}
	<div class="loading">Loading...</div>
{:else if error}
	<div class="error-message">{error}</div>
{:else if recipe}
	<div class="page">
		<div class="page-header">
			<div>
				<h1>{recipe.title}</h1>
				{#if recipe.description}
					<p class="description">{recipe.description}</p>
				{/if}
				{#if recipe.source_url}
					<a href={recipe.source_url} target="_blank" rel="noopener noreferrer" class="source-link">
						View original recipe
					</a>
				{/if}
			</div>
			<div class="header-actions">
				<button onclick={toggleFavorite} class="fav-btn" title={recipe.is_favorite ? 'Remove from favorites' : 'Add to favorites'}>
					{recipe.is_favorite ? '⭐' : '☆'}
				</button>
				<a href="/recipes/{recipe.id}/edit" class="btn btn-secondary">Edit</a>
				<button onclick={deleteRecipe} class="btn btn-danger">Delete</button>
			</div>
		</div>

		{#if recipe.images.length > 0}
			<div class="image-grid">
				{#each recipe.images as image}
					<img src={getImageUrl(image.id)} alt={recipe.title} class="recipe-image" />
				{/each}
			</div>
		{/if}

		<div class="meta-row">
			{#if recipe.prep_time_minutes}
				<div class="meta-item">
					<span class="meta-label">Prep:</span>
					<span class="meta-value">{recipe.prep_time_minutes} min</span>
				</div>
			{/if}
			{#if recipe.cook_time_minutes}
				<div class="meta-item">
					<span class="meta-label">Cook:</span>
					<span class="meta-value">{recipe.cook_time_minutes} min</span>
				</div>
			{/if}
			<div class="meta-item">
				<span class="meta-label">Servings:</span>
				<span class="meta-value">{recipe.servings}</span>
			</div>
			<span class="difficulty-badge {getDifficultyClass(recipe.difficulty)}">{recipe.difficulty}</span>
		</div>

		{#if recipe.dietary_tags.length > 0}
			<div class="tag-row">
				{#each recipe.dietary_tags as tag}
					<span class="dietary-tag {dietaryTagColors[tag]}">{dietaryTagLabels[tag]}</span>
				{/each}
			</div>
		{/if}

		{#if recipe.tags.length > 0}
			<div class="tag-row">
				{#each recipe.tags as tag}
					<span class="tag">{tag.name}</span>
				{/each}
			</div>
		{/if}

		<div class="content-grid">
			<Card>
				<CardHeader>
					<div class="ingredients-header">
						<CardTitle>Ingredients</CardTitle>
						<div class="scale-controls">
							<input type="number" bind:value={targetServings} min="1" class="input input-sm servings-input" />
							<button onclick={scaleRecipe} disabled={targetServings === recipe.servings} class="btn btn-sm btn-primary">
								Scale
							</button>
						</div>
					</div>
				</CardHeader>
				<CardContent>
					<ul class="ingredient-list">
						{#each scaledIngredients || recipe.ingredients as ing}
							<li>
								<span class="bullet">•</span>
								<span>
									{#if 'scaled_quantity' in ing}
										<span class="qty">{ing.scaled_quantity || ''}</span>
									{:else}
										<span class="qty">{ing.quantity || ''}</span>
									{/if}
									{ing.unit || ''}
									{ing.ingredient_name}
									{#if ing.notes}
										<span class="notes">({ing.notes})</span>
									{/if}
								</span>
							</li>
						{/each}
					</ul>
				</CardContent>
			</Card>

			<Card class="instructions-card">
				<CardHeader>
					<CardTitle>Instructions</CardTitle>
				</CardHeader>
				<CardContent>
					{#if recipe.instructions}
						<div class="instructions">{recipe.instructions}</div>
					{:else}
						<p class="empty">No instructions provided.</p>
					{/if}
				</CardContent>
			</Card>
		</div>

		{#if nutrition && (nutrition.calories || nutrition.protein || nutrition.carbs || nutrition.fat)}
			<Card>
				<CardHeader>
					<CardTitle>Nutrition Info <span class="subtitle">(for {targetServings} servings)</span></CardTitle>
				</CardHeader>
				<CardContent>
					<div class="nutrition-grid">
						{#if nutrition.calories}
							<div class="nutrition-item cal">
								<div class="nutrition-value">{nutrition.calories}</div>
								<div class="nutrition-label">Calories</div>
							</div>
						{/if}
						{#if nutrition.protein}
							<div class="nutrition-item protein">
								<div class="nutrition-value">{nutrition.protein}g</div>
								<div class="nutrition-label">Protein</div>
							</div>
						{/if}
						{#if nutrition.carbs}
							<div class="nutrition-item carbs">
								<div class="nutrition-value">{nutrition.carbs}g</div>
								<div class="nutrition-label">Carbs</div>
							</div>
						{/if}
						{#if nutrition.fat}
							<div class="nutrition-item fat">
								<div class="nutrition-value">{nutrition.fat}g</div>
								<div class="nutrition-label">Fat</div>
							</div>
						{/if}
						{#if nutrition.fiber}
							<div class="nutrition-item fiber">
								<div class="nutrition-value">{nutrition.fiber}g</div>
								<div class="nutrition-label">Fiber</div>
							</div>
						{/if}
					</div>
				</CardContent>
			</Card>
		{/if}

		{#if cost && cost.total_cost}
			<Card>
				<CardHeader>
					<CardTitle>Cost Estimate <span class="subtitle">(for {targetServings} servings)</span></CardTitle>
				</CardHeader>
				<CardContent>
					<div class="cost-grid">
						<div class="cost-summary">
							<div class="cost-row">
								<span class="cost-label">Total Cost:</span>
								<span class="cost-total">${cost.total_cost.toFixed(2)}</span>
							</div>
							{#if cost.cost_per_serving}
								<div class="cost-row">
									<span class="cost-label">Per Serving:</span>
									<span class="cost-per">${cost.cost_per_serving.toFixed(2)}</span>
								</div>
							{/if}
						</div>
						<div class="cost-breakdown">
							<h3>Ingredient Breakdown</h3>
							<div class="breakdown-list">
								{#each cost.ingredient_costs as item}
									<div class="breakdown-item">
										<span class="breakdown-name">{item.ingredient_name}</span>
										<span class="breakdown-cost">{item.cost ? `$${item.cost.toFixed(2)}` : '-'}</span>
									</div>
								{/each}
							</div>
						</div>
					</div>
				</CardContent>
			</Card>
		{/if}

		<Card>
			<CardHeader>
				<CardTitle>Cooking Timers</CardTitle>
			</CardHeader>
			<CardContent>
				<div class="quick-timers">
					<button onclick={() => quickTimer(5)} class="btn btn-sm btn-secondary">5 min</button>
					<button onclick={() => quickTimer(10)} class="btn btn-sm btn-secondary">10 min</button>
					<button onclick={() => quickTimer(15)} class="btn btn-sm btn-secondary">15 min</button>
					<button onclick={() => quickTimer(30)} class="btn btn-sm btn-secondary">30 min</button>
					{#if recipe.cook_time_minutes}
						<button onclick={() => quickTimer(recipe!.cook_time_minutes!)} class="btn btn-sm btn-primary">
							{recipe.cook_time_minutes} min (cook time)
						</button>
					{/if}
				</div>
				<div class="timer-form">
					<input type="text" bind:value={newTimerName} placeholder="Timer name" class="input" />
					<input type="number" bind:value={newTimerMinutes} min="1" class="input input-sm" />
					<span class="timer-unit">min</span>
					<button onclick={handleAddTimer} class="btn btn-primary">Add</button>
				</div>
				{#if timers.length > 0}
					<div class="timer-list">
						{#each timers as timer}
							<div class="timer-item" class:done={timer.remaining === 0}>
								<div class="timer-info">
									<span class="timer-name">{timer.name}</span>
									<span class="timer-time" class:alert={timer.remaining === 0}>{formatTime(timer.remaining)}</span>
								</div>
								<div class="timer-actions">
									{#if timer.isRunning && !timer.isPaused}
										<button onclick={() => pauseTimer(timer.id)} class="btn btn-sm btn-warning">Pause</button>
									{:else if timer.isPaused}
										<button onclick={() => resumeTimer(timer.id)} class="btn btn-sm btn-success">Resume</button>
									{:else if timer.remaining > 0}
										<button onclick={() => startTimer(timer.id)} class="btn btn-sm btn-success">Start</button>
									{/if}
									<button onclick={() => resetTimer(timer.id)} class="btn btn-sm btn-secondary">Reset</button>
									<button onclick={() => removeTimer(timer.id)} class="btn btn-sm btn-danger">Remove</button>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<p class="empty">No active timers. Add one above or use quick buttons.</p>
				{/if}
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<CardTitle>Personal Notes</CardTitle>
			</CardHeader>
			<CardContent>
				<div class="note-form">
					<textarea bind:value={newNoteContent} placeholder="Add a note about this recipe..." rows="2" class="input"></textarea>
					<button onclick={handleAddNote} disabled={!newNoteContent.trim()} class="btn btn-primary">Add Note</button>
				</div>
				{#if recipe.notes.length > 0}
					<div class="note-list">
						{#each recipe.notes as note}
							<div class="note-item">
								{#if editingNoteId === note.id}
									<div class="note-edit">
										<textarea bind:value={editingNoteContent} rows="2" class="input"></textarea>
										<div class="note-edit-actions">
											<button onclick={handleUpdateNote} class="btn btn-sm btn-success">Save</button>
											<button onclick={() => { editingNoteId = null; editingNoteContent = ''; }} class="btn btn-sm btn-secondary">Cancel</button>
										</div>
									</div>
								{:else}
									<div class="note-content">
										<p>{note.content}</p>
										<div class="note-actions">
											<button onclick={() => { editingNoteId = note.id; editingNoteContent = note.content; }} class="link-btn">Edit</button>
											<button onclick={() => handleDeleteNote(note.id)} class="link-btn danger">Delete</button>
										</div>
									</div>
									<p class="note-date">{new Date(note.created_at).toLocaleDateString()}</p>
								{/if}
							</div>
						{/each}
					</div>
				{:else}
					<p class="empty">No notes yet. Add your cooking tips and modifications above.</p>
				{/if}
			</CardContent>
		</Card>
	</div>
{/if}

<style>
	.page {
		max-width: 900px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--size-4);
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.description {
		color: var(--color-text-muted);
		margin: var(--size-2) 0 0 0;
	}

	.source-link {
		font-size: var(--font-size-0);
		color: var(--color-primary);
		text-decoration: none;
	}

	.source-link:hover {
		text-decoration: underline;
	}

	.header-actions {
		display: flex;
		gap: var(--size-2);
		align-items: center;
	}

	.fav-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: var(--font-size-5);
		transition: transform 0.2s;
	}

	.fav-btn:hover {
		transform: scale(1.1);
	}

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		border: none;
	}

	.btn-sm {
		padding: var(--size-1) var(--size-3);
		font-size: var(--font-size-0);
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: var(--color-accent);
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-border);
	}

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.btn-warning {
		background: rgba(235, 203, 139, 0.3);
		color: #d08770;
	}

	.btn-warning:hover {
		background: rgba(235, 203, 139, 0.4);
	}

	.btn-danger {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
	}

	.btn-danger:hover {
		background: rgba(191, 97, 106, 0.3);
	}

	.loading {
		text-align: center;
		padding: var(--size-8) 0;
	}

	.error-message {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
		padding: var(--size-4);
		border-radius: var(--radius-2);
	}

	.image-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: var(--size-4);
	}

	.recipe-image {
		width: 100%;
		height: 250px;
		object-fit: cover;
		border-radius: var(--radius-2);
	}

	.meta-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-4);
		font-size: var(--font-size-1);
		align-items: center;
	}

	.meta-item {
		display: flex;
		align-items: center;
		gap: var(--size-1);
	}

	.meta-label {
		color: var(--color-text-muted);
	}

	.meta-value {
		font-weight: var(--font-weight-6);
	}

	.difficulty-badge {
		padding: var(--size-1) var(--size-2);
		border-radius: 9999px;
		font-size: var(--font-size-0);
		text-transform: capitalize;
	}

	.diff-easy {
		background: rgba(163, 190, 140, 0.2);
		color: #a3be8c;
	}

	.diff-medium {
		background: rgba(235, 203, 139, 0.2);
		color: #ebcb8b;
	}

	.diff-hard {
		background: rgba(191, 97, 106, 0.2);
		color: #bf616a;
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-2);
	}

	.tag {
		padding: var(--size-1) var(--size-3);
		background: var(--color-accent);
		color: var(--color-text-muted);
		border-radius: 9999px;
		font-size: var(--font-size-0);
	}

	.dietary-tag {
		padding: var(--size-1) var(--size-3);
		border-radius: 9999px;
		font-size: var(--font-size-0);
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: var(--size-6);
	}

	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
		}
	}

	.ingredients-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
	}

	.scale-controls {
		display: flex;
		align-items: center;
		gap: var(--size-2);
	}

	.servings-input {
		width: 60px;
		text-align: center;
	}

	.input {
		width: 100%;
		padding: var(--size-2) var(--size-4);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		background: var(--color-bg);
		color: var(--color-text);
	}

	.input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.input-sm {
		padding: var(--size-1) var(--size-2);
		font-size: var(--font-size-0);
	}

	.ingredient-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: var(--size-2);
	}

	.ingredient-list li {
		display: flex;
		align-items: flex-start;
		gap: var(--size-2);
	}

	.bullet {
		color: var(--color-text-muted);
	}

	.qty {
		font-weight: var(--font-weight-6);
	}

	.notes {
		color: var(--color-text-muted);
	}

	.instructions {
		white-space: pre-wrap;
		line-height: 1.6;
	}

	.empty {
		color: var(--color-text-muted);
		font-size: var(--font-size-1);
	}

	.subtitle {
		font-size: var(--font-size-0);
		font-weight: normal;
		color: var(--color-text-muted);
	}

	.nutrition-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
		gap: var(--size-4);
	}

	.nutrition-item {
		text-align: center;
		padding: var(--size-3);
		border-radius: var(--radius-2);
	}

	.nutrition-item.cal { background: rgba(208, 135, 112, 0.1); }
	.nutrition-item.protein { background: rgba(191, 97, 106, 0.1); }
	.nutrition-item.carbs { background: rgba(129, 161, 193, 0.1); }
	.nutrition-item.fat { background: rgba(235, 203, 139, 0.1); }
	.nutrition-item.fiber { background: rgba(163, 190, 140, 0.1); }

	.nutrition-value {
		font-size: var(--font-size-4);
		font-weight: var(--font-weight-7);
	}

	.nutrition-item.cal .nutrition-value { color: #d08770; }
	.nutrition-item.protein .nutrition-value { color: #bf616a; }
	.nutrition-item.carbs .nutrition-value { color: #81a1c1; }
	.nutrition-item.fat .nutrition-value { color: #ebcb8b; }
	.nutrition-item.fiber .nutrition-value { color: #a3be8c; }

	.nutrition-label {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.cost-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--size-6);
	}

	@media (max-width: 600px) {
		.cost-grid {
			grid-template-columns: 1fr;
		}
	}

	.cost-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--size-2);
	}

	.cost-label {
		color: var(--color-text-muted);
	}

	.cost-total {
		font-size: var(--font-size-4);
		font-weight: var(--font-weight-7);
		color: var(--color-success);
	}

	.cost-per {
		font-size: var(--font-size-2);
		font-weight: var(--font-weight-6);
	}

	.cost-breakdown h3 {
		font-size: var(--font-size-0);
		font-weight: var(--font-weight-6);
		margin: 0 0 var(--size-2) 0;
	}

	.breakdown-list {
		max-height: 120px;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.breakdown-item {
		display: flex;
		justify-content: space-between;
		font-size: var(--font-size-0);
	}

	.breakdown-name {
		color: var(--color-text-muted);
	}

	.breakdown-cost {
		font-weight: var(--font-weight-6);
	}

	.quick-timers {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-2);
		margin-bottom: var(--size-4);
	}

	.timer-form {
		display: flex;
		gap: var(--size-2);
		align-items: center;
		margin-bottom: var(--size-4);
	}

	.timer-form .input:first-of-type {
		flex: 1;
	}

	.timer-form .input-sm {
		width: 70px;
	}

	.timer-unit {
		color: var(--color-text-muted);
	}

	.timer-list {
		display: flex;
		flex-direction: column;
		gap: var(--size-2);
	}

	.timer-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--size-3);
		background: var(--color-bg-muted);
		border-radius: var(--radius-2);
	}

	.timer-item.done {
		background: rgba(191, 97, 106, 0.1);
	}

	.timer-info {
		display: flex;
		align-items: center;
		gap: var(--size-3);
	}

	.timer-name {
		font-weight: var(--font-weight-6);
	}

	.timer-time {
		font-family: monospace;
		font-size: var(--font-size-4);
	}

	.timer-time.alert {
		color: var(--color-error);
	}

	.timer-actions {
		display: flex;
		gap: var(--size-2);
	}

	.note-form {
		display: flex;
		gap: var(--size-2);
		align-items: flex-end;
		margin-bottom: var(--size-4);
	}

	.note-form textarea {
		flex: 1;
	}

	.note-list {
		display: flex;
		flex-direction: column;
		gap: var(--size-3);
	}

	.note-item {
		padding: var(--size-3);
		background: var(--color-bg-muted);
		border-radius: var(--radius-2);
	}

	.note-content {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.note-content p {
		margin: 0;
		white-space: pre-wrap;
	}

	.note-actions {
		display: flex;
		gap: var(--size-2);
	}

	.note-date {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		margin: var(--size-1) 0 0 0;
	}

	.note-edit {
		display: flex;
		gap: var(--size-2);
	}

	.note-edit textarea {
		flex: 1;
	}

	.note-edit-actions {
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.link-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-text-muted);
		font-size: var(--font-size-0);
	}

	.link-btn:hover {
		color: var(--color-text);
	}

	.link-btn.danger {
		color: var(--color-error);
	}
</style>
