<script lang="ts">
	import type { Recipe, ScaledIngredient } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let recipe: Recipe | null = $state(null);
	let scaledIngredients: ScaledIngredient[] | null = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let targetServings = $state(4);

	$effect(() => {
		if (recipe) {
			targetServings = recipe.servings;
		}
	});

	onMount(async () => {
		try {
			recipe = await api.get<Recipe>(`/recipes/${$page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipe';
		} finally {
			loading = false;
		}
	});

	async function scaleRecipe() {
		if (!recipe) return;
		try {
			scaledIngredients = await api.get<ScaledIngredient[]>(
				`/recipes/${recipe.id}/scale/${targetServings}`
			);
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
	</div>
{/if}
