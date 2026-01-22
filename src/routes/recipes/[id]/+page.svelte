<script lang="ts">
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

	const difficultyColors = {
		easy: 'bg-green-100 text-green-800',
		medium: 'bg-yellow-100 text-yellow-800',
		hard: 'bg-red-100 text-red-800'
	};
</script>

{#if loading}
	<div class="text-center py-12">Loading...</div>
{:else if error}
	<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
{:else if recipe}
	<div class="max-w-4xl mx-auto space-y-6">
		<div class="flex items-start justify-between">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">{recipe.title}</h1>
				{#if recipe.description}
					<p class="text-gray-600 mt-2">{recipe.description}</p>
				{/if}
				{#if recipe.source_url}
					<a
						href={recipe.source_url}
						target="_blank"
						rel="noopener noreferrer"
						class="text-sm text-blue-600 hover:underline mt-1 inline-block"
					>
						View original recipe
					</a>
				{/if}
			</div>
			<div class="flex gap-2">
				<button
					onclick={toggleFavorite}
					class="p-2 text-2xl hover:scale-110 transition-transform"
					title={recipe.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
				>
					{recipe.is_favorite ? '⭐' : '☆'}
				</button>
				<a
					href="/recipes/{recipe.id}/edit"
					class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
				>
					Edit
				</a>
				<button
					onclick={deleteRecipe}
					class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
				>
					Delete
				</button>
			</div>
		</div>

		{#if recipe.images.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each recipe.images as image}
					<img
						src={getImageUrl(image.id)}
						alt={recipe.title}
						class="w-full h-64 object-cover rounded-lg"
					/>
				{/each}
			</div>
		{/if}

		<div class="flex flex-wrap gap-4 text-sm">
			{#if recipe.prep_time_minutes}
				<div class="flex items-center gap-1">
					<span class="text-gray-500">Prep:</span>
					<span class="font-medium">{recipe.prep_time_minutes} min</span>
				</div>
			{/if}
			{#if recipe.cook_time_minutes}
				<div class="flex items-center gap-1">
					<span class="text-gray-500">Cook:</span>
					<span class="font-medium">{recipe.cook_time_minutes} min</span>
				</div>
			{/if}
			<div class="flex items-center gap-1">
				<span class="text-gray-500">Servings:</span>
				<span class="font-medium">{recipe.servings}</span>
			</div>
			<span class="px-2 py-0.5 rounded-full text-xs {difficultyColors[recipe.difficulty]}">
				{recipe.difficulty}
			</span>
		</div>

		{#if recipe.dietary_tags.length > 0}
			<div class="flex flex-wrap gap-2">
				{#each recipe.dietary_tags as tag}
					<span class="px-3 py-1 rounded-full text-sm {dietaryTagColors[tag]}">
						{dietaryTagLabels[tag]}
					</span>
				{/each}
			</div>
		{/if}

		{#if recipe.tags.length > 0}
			<div class="flex flex-wrap gap-2">
				{#each recipe.tags as tag}
					<span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">{tag.name}</span>
				{/each}
			</div>
		{/if}

		<div class="grid md:grid-cols-3 gap-6">
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold">Ingredients</h2>
					<div class="flex items-center gap-2">
						<input
							type="number"
							bind:value={targetServings}
							min="1"
							class="w-16 px-2 py-1 border rounded text-center"
						/>
						<button
							onclick={scaleRecipe}
							disabled={targetServings === recipe.servings}
							class="px-2 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
						>
							Scale
						</button>
					</div>
				</div>
				<ul class="space-y-2">
					{#each scaledIngredients || recipe.ingredients as ing}
						<li class="flex items-start gap-2">
							<span class="text-gray-400">•</span>
							<span>
								{#if 'scaled_quantity' in ing}
									<span class="font-medium">{ing.scaled_quantity || ''}</span>
								{:else}
									<span class="font-medium">{ing.quantity || ''}</span>
								{/if}
								{ing.unit || ''}
								{ing.ingredient_name}
								{#if ing.notes}
									<span class="text-gray-500">({ing.notes})</span>
								{/if}
							</span>
						</li>
					{/each}
				</ul>
			</div>

			<div class="md:col-span-2 bg-white p-6 rounded-lg shadow-sm border">
				<h2 class="text-lg font-semibold mb-4">Instructions</h2>
				{#if recipe.instructions}
					<div class="prose prose-sm max-w-none whitespace-pre-wrap">
						{recipe.instructions}
					</div>
				{:else}
					<p class="text-gray-500">No instructions provided.</p>
				{/if}
			</div>
		</div>

		{#if nutrition && (nutrition.calories || nutrition.protein || nutrition.carbs || nutrition.fat)}
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<h2 class="text-lg font-semibold mb-4">
					Nutrition Info
					<span class="text-sm font-normal text-gray-500">(for {targetServings} servings)</span>
				</h2>
				<div class="grid grid-cols-2 md:grid-cols-5 gap-4">
					{#if nutrition.calories}
						<div class="text-center p-3 bg-orange-50 rounded-lg">
							<div class="text-2xl font-bold text-orange-600">{nutrition.calories}</div>
							<div class="text-sm text-gray-600">Calories</div>
						</div>
					{/if}
					{#if nutrition.protein}
						<div class="text-center p-3 bg-red-50 rounded-lg">
							<div class="text-2xl font-bold text-red-600">{nutrition.protein}g</div>
							<div class="text-sm text-gray-600">Protein</div>
						</div>
					{/if}
					{#if nutrition.carbs}
						<div class="text-center p-3 bg-blue-50 rounded-lg">
							<div class="text-2xl font-bold text-blue-600">{nutrition.carbs}g</div>
							<div class="text-sm text-gray-600">Carbs</div>
						</div>
					{/if}
					{#if nutrition.fat}
						<div class="text-center p-3 bg-yellow-50 rounded-lg">
							<div class="text-2xl font-bold text-yellow-600">{nutrition.fat}g</div>
							<div class="text-sm text-gray-600">Fat</div>
						</div>
					{/if}
					{#if nutrition.fiber}
						<div class="text-center p-3 bg-green-50 rounded-lg">
							<div class="text-2xl font-bold text-green-600">{nutrition.fiber}g</div>
							<div class="text-sm text-gray-600">Fiber</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		{#if cost && cost.total_cost}
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<h2 class="text-lg font-semibold mb-4">
					Cost Estimate
					<span class="text-sm font-normal text-gray-500">(for {targetServings} servings)</span>
				</h2>
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<div class="flex justify-between items-center mb-2">
							<span class="text-gray-600">Total Cost:</span>
							<span class="text-2xl font-bold text-green-600">${cost.total_cost.toFixed(2)}</span>
						</div>
						{#if cost.cost_per_serving}
							<div class="flex justify-between items-center">
								<span class="text-gray-600">Per Serving:</span>
								<span class="text-lg font-semibold text-gray-900">
									${cost.cost_per_serving.toFixed(2)}
								</span>
							</div>
						{/if}
					</div>
					<div>
						<h3 class="text-sm font-medium text-gray-700 mb-2">Ingredient Breakdown</h3>
						<div class="space-y-1 max-h-32 overflow-y-auto">
							{#each cost.ingredient_costs as item}
								<div class="flex justify-between text-sm">
									<span class="text-gray-600">{item.ingredient_name}</span>
									<span class="font-medium">
										{item.cost ? `$${item.cost.toFixed(2)}` : '-'}
									</span>
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		{/if}

		<div class="bg-white p-6 rounded-lg shadow-sm border">
			<h2 class="text-lg font-semibold mb-4">Cooking Timers</h2>
			<div class="flex flex-wrap gap-2 mb-4">
				<button
					onclick={() => quickTimer(5)}
					class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
				>
					5 min
				</button>
				<button
					onclick={() => quickTimer(10)}
					class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
				>
					10 min
				</button>
				<button
					onclick={() => quickTimer(15)}
					class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
				>
					15 min
				</button>
				<button
					onclick={() => quickTimer(30)}
					class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
				>
					30 min
				</button>
				{#if recipe.cook_time_minutes}
					<button
						onclick={() => quickTimer(recipe!.cook_time_minutes!)}
						class="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
					>
						{recipe.cook_time_minutes} min (cook time)
					</button>
				{/if}
			</div>
			<div class="flex gap-2 mb-4">
				<input
					type="text"
					bind:value={newTimerName}
					placeholder="Timer name"
					class="flex-1 px-3 py-2 border rounded-lg"
				/>
				<input
					type="number"
					bind:value={newTimerMinutes}
					min="1"
					class="w-20 px-3 py-2 border rounded-lg"
				/>
				<span class="self-center text-gray-500">min</span>
				<button
					onclick={handleAddTimer}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Add
				</button>
			</div>
			{#if timers.length > 0}
				<div class="space-y-2">
					{#each timers as timer}
						<div
							class="flex items-center justify-between p-3 rounded-lg {timer.remaining === 0
								? 'bg-red-50'
								: 'bg-gray-50'}"
						>
							<div>
								<span class="font-medium">{timer.name}</span>
								<span
									class="ml-2 text-2xl font-mono {timer.remaining === 0
										? 'text-red-600'
										: 'text-gray-900'}"
								>
									{formatTime(timer.remaining)}
								</span>
							</div>
							<div class="flex gap-2">
								{#if timer.isRunning && !timer.isPaused}
									<button
										onclick={() => pauseTimer(timer.id)}
										class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
									>
										Pause
									</button>
								{:else if timer.isPaused}
									<button
										onclick={() => resumeTimer(timer.id)}
										class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
									>
										Resume
									</button>
								{:else if timer.remaining > 0}
									<button
										onclick={() => startTimer(timer.id)}
										class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
									>
										Start
									</button>
								{/if}
								<button
									onclick={() => resetTimer(timer.id)}
									class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
								>
									Reset
								</button>
								<button
									onclick={() => removeTimer(timer.id)}
									class="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
								>
									Remove
								</button>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 text-sm">No active timers. Add one above or use quick buttons.</p>
			{/if}
		</div>

		<div class="bg-white p-6 rounded-lg shadow-sm border">
			<h2 class="text-lg font-semibold mb-4">Personal Notes</h2>
			<div class="flex gap-2 mb-4">
				<textarea
					bind:value={newNoteContent}
					placeholder="Add a note about this recipe (cooking tips, modifications, etc.)"
					rows="2"
					class="flex-1 px-3 py-2 border rounded-lg"
				></textarea>
				<button
					onclick={handleAddNote}
					disabled={!newNoteContent.trim()}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 self-end"
				>
					Add Note
				</button>
			</div>
			{#if recipe.notes.length > 0}
				<div class="space-y-3">
					{#each recipe.notes as note}
						<div class="p-3 bg-gray-50 rounded-lg">
							{#if editingNoteId === note.id}
								<div class="flex gap-2">
									<textarea
										bind:value={editingNoteContent}
										rows="2"
										class="flex-1 px-3 py-2 border rounded-lg"
									></textarea>
									<div class="flex flex-col gap-1">
										<button
											onclick={handleUpdateNote}
											class="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
										>
											Save
										</button>
										<button
											onclick={() => {
												editingNoteId = null;
												editingNoteContent = '';
											}}
											class="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
										>
											Cancel
										</button>
									</div>
								</div>
							{:else}
								<div class="flex justify-between items-start">
									<p class="whitespace-pre-wrap">{note.content}</p>
									<div class="flex gap-1 ml-2">
										<button
											onclick={() => {
												editingNoteId = note.id;
												editingNoteContent = note.content;
											}}
											class="px-2 py-1 text-gray-500 hover:text-gray-700 text-sm"
										>
											Edit
										</button>
										<button
											onclick={() => handleDeleteNote(note.id)}
											class="px-2 py-1 text-red-500 hover:text-red-700 text-sm"
										>
											Delete
										</button>
									</div>
								</div>
								<p class="text-xs text-gray-400 mt-1">
									{new Date(note.created_at).toLocaleDateString()}
								</p>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-gray-500 text-sm">
					No notes yet. Add your cooking tips and modifications above.
				</p>
			{/if}
		</div>
	</div>
{/if}
