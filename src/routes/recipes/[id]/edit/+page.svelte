<script lang="ts">
	import type { Recipe, Ingredient, Tag, DifficultyLevel } from '$lib/types';
	import { api, uploadImage } from '$lib/utils';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let recipe: Recipe | null = $state(null);
	let ingredients: Ingredient[] = $state([]);
	let tags: Tag[] = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);

	let title = $state('');
	let description = $state('');
	let instructions = $state('');
	let prepTime = $state<number | null>(null);
	let cookTime = $state<number | null>(null);
	let servings = $state(4);
	let difficulty = $state<DifficultyLevel>('medium');
	let selectedTagIds = $state<number[]>([]);

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
			[recipe, ingredients, tags] = await Promise.all([
				api.get<Recipe>(`/recipes/${$page.params.id}`),
				api.get<Ingredient[]>('/ingredients'),
				api.get<Tag[]>('/tags')
			]);

			title = recipe.title;
			description = recipe.description || '';
			instructions = recipe.instructions || '';
			prepTime = recipe.prep_time_minutes;
			cookTime = recipe.cook_time_minutes;
			servings = recipe.servings;
			difficulty = recipe.difficulty;
			selectedTagIds = recipe.tags.map((t) => t.id);
			recipeIngredients = recipe.ingredients.map((ri) => ({
				ingredient_id: ri.ingredient_id,
				quantity: ri.quantity || '',
				unit: ri.unit || '',
				notes: ri.notes || ''
			}));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipe';
		} finally {
			loading = false;
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

	async function handleSubmit() {
		if (!title.trim() || !recipe) {
			error = 'Title is required';
			return;
		}

		saving = true;
		error = null;

		try {
			await api.put(`/recipes/${recipe.id}`, {
				title,
				description: description || null,
				instructions: instructions || null,
				prep_time_minutes: prepTime,
				cook_time_minutes: cookTime,
				servings,
				difficulty,
				tag_ids: selectedTagIds,
				ingredients: recipeIngredients.filter((ri) => ri.ingredient_id)
			});

			if (imageFile) {
				await uploadImage(recipe.id, imageFile, true);
			}

			goto(`/recipes/${recipe.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update recipe';
		} finally {
			saving = false;
		}
	}
</script>

{#if loading}
	<div class="text-center py-12">Loading...</div>
{:else if !recipe}
	<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error || 'Recipe not found'}</div>
{:else}
	<div class="max-w-3xl mx-auto space-y-6">
		<h1 class="text-3xl font-bold text-gray-900">Edit Recipe</h1>

		{#if error}
			<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
		{/if}

		<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6">
			<div class="bg-white p-6 rounded-lg shadow-sm border space-y-4">
				<div>
					<label for="title" class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
					<input
						id="title"
						type="text"
						bind:value={title}
						required
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>

				<div>
					<label for="description" class="block text-sm font-medium text-gray-700 mb-1">
						Description
					</label>
					<textarea
						id="description"
						bind:value={description}
						rows="2"
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					></textarea>
				</div>

				<div>
					<label for="instructions" class="block text-sm font-medium text-gray-700 mb-1">
						Instructions
					</label>
					<textarea
						id="instructions"
						bind:value={instructions}
						rows="6"
						class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					></textarea>
				</div>

				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div>
						<label for="prepTime" class="block text-sm font-medium text-gray-700 mb-1">
							Prep (min)
						</label>
						<input
							id="prepTime"
							type="number"
							bind:value={prepTime}
							min="0"
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="cookTime" class="block text-sm font-medium text-gray-700 mb-1">
							Cook (min)
						</label>
						<input
							id="cookTime"
							type="number"
							bind:value={cookTime}
							min="0"
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="servings" class="block text-sm font-medium text-gray-700 mb-1">
							Servings
						</label>
						<input
							id="servings"
							type="number"
							bind:value={servings}
							min="1"
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="difficulty" class="block text-sm font-medium text-gray-700 mb-1">
							Difficulty
						</label>
						<select
							id="difficulty"
							bind:value={difficulty}
							class="w-full px-4 py-2 border rounded-lg"
						>
							<option value="easy">Easy</option>
							<option value="medium">Medium</option>
							<option value="hard">Hard</option>
						</select>
					</div>
				</div>

				<div>
					<label for="image" class="block text-sm font-medium text-gray-700 mb-1">
						Add Image
					</label>
					<input
						id="image"
						type="file"
						accept="image/jpeg,image/png,image/webp"
						onchange={(e) => {
							const input = e.target as HTMLInputElement;
							imageFile = input.files?.[0] || null;
						}}
						class="w-full px-4 py-2 border rounded-lg"
					/>
				</div>

				{#if tags.length > 0}
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
						<div class="flex flex-wrap gap-2">
							{#each tags as tag}
								<button
									type="button"
									class="px-3 py-1 rounded-full text-sm {selectedTagIds.includes(tag.id)
										? 'bg-blue-600 text-white'
										: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
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

			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold">Ingredients</h2>
					<button
						type="button"
						onclick={addIngredient}
						disabled={ingredients.length === 0}
						class="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
					>
						+ Add
					</button>
				</div>

				<div class="space-y-3">
					{#each recipeIngredients as ri, index}
						<div class="flex gap-2 items-start">
							<select bind:value={ri.ingredient_id} class="flex-1 px-3 py-2 border rounded-lg">
								{#each ingredients as ing}
									<option value={ing.id}>{ing.name}</option>
								{/each}
							</select>
							<input
								type="text"
								bind:value={ri.quantity}
								placeholder="Qty"
								class="w-20 px-3 py-2 border rounded-lg"
							/>
							<input
								type="text"
								bind:value={ri.unit}
								placeholder="Unit"
								class="w-20 px-3 py-2 border rounded-lg"
							/>
							<input
								type="text"
								bind:value={ri.notes}
								placeholder="Notes"
								class="flex-1 px-3 py-2 border rounded-lg"
							/>
							<button
								type="button"
								onclick={() => removeIngredient(index)}
								class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
							>
								×
							</button>
						</div>
					{/each}
				</div>
			</div>

			<div class="flex gap-4">
				<button
					type="submit"
					disabled={saving}
					class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
				>
					{saving ? 'Saving...' : 'Save Changes'}
				</button>
				<a
					href="/recipes/{recipe.id}"
					class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
				>
					Cancel
				</a>
			</div>
		</form>
	</div>
{/if}
