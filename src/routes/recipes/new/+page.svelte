<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
	import type { Ingredient, Tag, DifficultyLevel, DietaryTag } from '$lib/types';
	import { api, uploadImage } from '$lib/utils';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { allDietaryTags, dietaryTagLabels } from '$lib/constants/dietary-tags';

	let ingredients: Ingredient[] = $state([]);
	let tags: Tag[] = $state([]);
	let loading = $state(false);
	let error = $state<string | null>(null);

	let title = $state('');
	let description = $state('');
	let instructions = $state('');
	let prepTime = $state<number | null>(null);
	let cookTime = $state<number | null>(null);
	let servings = $state(4);
	let difficulty = $state<DifficultyLevel>('medium');
	let selectedTagIds = $state<number[]>([]);
	let selectedDietaryTags = $state<DietaryTag[]>([]);
	let sourceUrl = $state('');

	let recipeIngredients = $state<
		Array<{
			ingredient_id: number;
			quantity: string;
			unit: string;
			notes: string;
		}>
	>([]);

	let imageFile: File | null = $state(null);

	onMount(async () => {
		try {
			[ingredients, tags] = await Promise.all([
				api.get<Ingredient[]>('/ingredients'),
				api.get<Tag[]>('/tags')
			]);
		} catch {
			/* ignore */
		}
	});

	function addIngredient() {
		if (ingredients.length > 0) {
			recipeIngredients = [
				...recipeIngredients,
				{ ingredient_id: ingredients[0].id, quantity: '', unit: '', notes: '' }
			];
		}
	}

	function removeIngredient(index: number) {
		recipeIngredients = recipeIngredients.filter((_, i) => i !== index);
	}

	function toggleDietaryTag(tag: DietaryTag) {
		if (selectedDietaryTags.includes(tag)) {
			selectedDietaryTags = selectedDietaryTags.filter((t) => t !== tag);
		} else {
			selectedDietaryTags = [...selectedDietaryTags, tag];
		}
	}

	async function handleSubmit() {
		if (!title.trim()) {
			error = 'Title is required';
			return;
		}

		loading = true;
		error = null;

		try {
			const recipe = await api.post<{ id: number }>('/recipes', {
				title,
				description: description || null,
				instructions: instructions || null,
				prep_time_minutes: prepTime,
				cook_time_minutes: cookTime,
				servings,
				difficulty,
				dietary_tags: selectedDietaryTags,
				source_url: sourceUrl || null,
				tag_ids: selectedTagIds,
				ingredients: recipeIngredients.filter((ri) => ri.ingredient_id)
			});

			if (imageFile) {
				await uploadImage(recipe.id, imageFile, true);
			}

			goto(`/recipes/${recipe.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create recipe';
		} finally {
			loading = false;
		}
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>New Recipe</h1>
		<a href="/recipes/import" class="btn btn-success">Import from URL</a>
	</div>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="form">
		<Card>
			<CardHeader>
				<CardTitle>Basic Info</CardTitle>
			</CardHeader>
			<CardContent>
				<div class="form-content">
					<div class="form-group">
						<label for="title">Title *</label>
						<input id="title" type="text" bind:value={title} required class="input" />
					</div>

					<div class="form-group">
						<label for="description">Description</label>
						<textarea id="description" bind:value={description} rows="2" class="input"></textarea>
					</div>

					<div class="form-group">
						<label for="instructions">Instructions</label>
						<textarea id="instructions" bind:value={instructions} rows="6" placeholder="Step by step instructions..." class="input"></textarea>
					</div>

					<div class="form-grid">
						<div class="form-group">
							<label for="prepTime">Prep (min)</label>
							<input id="prepTime" type="number" bind:value={prepTime} min="0" class="input" />
						</div>
						<div class="form-group">
							<label for="cookTime">Cook (min)</label>
							<input id="cookTime" type="number" bind:value={cookTime} min="0" class="input" />
						</div>
						<div class="form-group">
							<label for="servings">Servings</label>
							<input id="servings" type="number" bind:value={servings} min="1" class="input" />
						</div>
						<div class="form-group">
							<label for="difficulty">Difficulty</label>
							<select id="difficulty" bind:value={difficulty} class="input">
								<option value="easy">Easy</option>
								<option value="medium">Medium</option>
								<option value="hard">Hard</option>
							</select>
						</div>
					</div>

					<div class="form-group">
						<label for="sourceUrl">Source URL (optional)</label>
						<input id="sourceUrl" type="url" bind:value={sourceUrl} placeholder="https://example.com/recipe" class="input" />
					</div>

					<div class="form-group">
						<label for="image">Image</label>
						<input
							id="image"
							type="file"
							accept="image/jpeg,image/png,image/webp"
							onchange={(e) => {
								const input = e.target as HTMLInputElement;
								imageFile = input.files?.[0] || null;
							}}
							class="input"
						/>
					</div>

					<div class="form-group">
						<span class="label">Dietary Tags</span>
						<div class="tag-selector">
							{#each allDietaryTags as tag}
								<button
									type="button"
									class="tag-btn"
									class:selected={selectedDietaryTags.includes(tag)}
									onclick={() => toggleDietaryTag(tag)}
								>
									{dietaryTagLabels[tag]}
								</button>
							{/each}
						</div>
					</div>

					{#if tags.length > 0}
						<div class="form-group">
							<span class="label">Tags</span>
							<div class="tag-selector">
								{#each tags as tag}
									<button
										type="button"
										class="tag-btn tag-custom"
										class:selected={selectedTagIds.includes(tag.id)}
										onclick={() => {
											if (selectedTagIds.includes(tag.id)) {
												selectedTagIds = selectedTagIds.filter((id) => id !== tag.id);
											} else {
												selectedTagIds = [...selectedTagIds, tag.id];
											}
										}}
									>
										{tag.name}
									</button>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</CardContent>
		</Card>

		<Card>
			<CardHeader>
				<div class="section-header">
					<CardTitle>Ingredients</CardTitle>
					<button type="button" onclick={addIngredient} disabled={ingredients.length === 0} class="btn btn-sm btn-secondary">
						+ Add
					</button>
				</div>
			</CardHeader>
			<CardContent>
				{#if ingredients.length === 0}
					<p class="empty">
						No ingredients available. <a href="/ingredients" class="link">Add some first.</a>
					</p>
				{:else}
					<div class="ingredient-list">
						{#each recipeIngredients as ri, index}
							<div class="ingredient-row">
								<select bind:value={ri.ingredient_id} class="input">
									{#each ingredients as ing}
										<option value={ing.id}>{ing.name}</option>
									{/each}
								</select>
								<input type="text" bind:value={ri.quantity} placeholder="Qty" class="input input-sm" />
								<input type="text" bind:value={ri.unit} placeholder="Unit" class="input input-sm" />
								<input type="text" bind:value={ri.notes} placeholder="Notes" class="input" />
								<button type="button" onclick={() => removeIngredient(index)} class="btn-remove">×</button>
							</div>
						{/each}
					</div>
				{/if}
			</CardContent>
		</Card>

		<div class="form-actions">
			<button type="submit" disabled={loading} class="btn btn-primary">
				{loading ? 'Creating...' : 'Create Recipe'}
			</button>
			<a href="/recipes" class="btn btn-secondary">Cancel</a>
		</div>
	</form>
</div>

<style>
	.page {
		max-width: 800px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.form-content {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.form-group label,
	.form-group .label {
		font-size: var(--font-size-0);
		font-weight: var(--font-weight-6);
	}

	.form-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--size-4);
	}

	@media (max-width: 768px) {
		.form-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
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
		width: 80px;
		flex-shrink: 0;
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

	.btn-secondary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.error-message {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
		padding: var(--size-4);
		border-radius: var(--radius-2);
	}

	.tag-selector {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-2);
	}

	.tag-btn {
		padding: var(--size-1) var(--size-3);
		border-radius: 9999px;
		font-size: var(--font-size-0);
		cursor: pointer;
		border: none;
		background: var(--color-accent);
		color: var(--color-text-muted);
		transition: all 0.2s;
	}

	.tag-btn:hover {
		background: var(--color-border);
	}

	.tag-btn.selected {
		background: var(--color-success);
		color: var(--nord6);
	}

	.tag-btn.tag-custom.selected {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.ingredient-list {
		display: flex;
		flex-direction: column;
		gap: var(--size-3);
	}

	.ingredient-row {
		display: flex;
		gap: var(--size-2);
		align-items: center;
	}

	.ingredient-row select {
		flex: 1;
	}

	.ingredient-row input:last-of-type {
		flex: 1;
	}

	.btn-remove {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-error);
		font-size: var(--font-size-3);
		padding: var(--size-1) var(--size-2);
		border-radius: var(--radius-2);
	}

	.btn-remove:hover {
		background: rgba(191, 97, 106, 0.1);
	}

	.empty {
		color: var(--color-text-muted);
		font-size: var(--font-size-1);
	}

	.link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
	}

	.form-actions {
		display: flex;
		gap: var(--size-4);
	}
</style>
