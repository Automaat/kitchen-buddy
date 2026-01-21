<script lang="ts">
	import type { RecipeListItem } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { onMount } from 'svelte';

	let recipes: RecipeListItem[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadFavorites() {
		loading = true;
		error = null;
		try {
			recipes = await api.get<RecipeListItem[]>('/favorites');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load favorites';
		} finally {
			loading = false;
		}
	}

	onMount(loadFavorites);

	async function removeFavorite(recipe: RecipeListItem) {
		try {
			await api.delete(`/favorites/${recipe.id}`);
			recipes = recipes.filter((r) => r.id !== recipe.id);
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

<div class="space-y-6">
	<h1 class="text-3xl font-bold text-gray-900">Favorites</h1>

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{:else if recipes.length === 0}
		<div class="text-center py-12 text-gray-500">
			No favorite recipes yet.
			<a href="/recipes" class="text-blue-600 hover:underline">Browse recipes</a>
			and mark some as favorites!
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each recipes as recipe}
				<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
					<a href="/recipes/{recipe.id}">
						{#if recipe.primary_image_id}
							<img
								src={getImageUrl(recipe.primary_image_id)}
								alt={recipe.title}
								class="w-full h-48 object-cover"
							/>
						{:else}
							<div class="w-full h-48 bg-gray-100 flex items-center justify-center text-4xl">
								🍽️
							</div>
						{/if}
					</a>
					<div class="p-4">
						<div class="flex items-start justify-between">
							<a href="/recipes/{recipe.id}" class="font-semibold text-lg hover:text-blue-600">
								{recipe.title}
							</a>
							<button
								onclick={() => removeFavorite(recipe)}
								class="text-xl hover:scale-110 transition-transform"
								title="Remove from favorites"
							>
								⭐
							</button>
						</div>
						{#if recipe.description}
							<p class="text-gray-600 text-sm mt-1 line-clamp-2">{recipe.description}</p>
						{/if}
						<div class="flex items-center gap-2 mt-3 text-sm text-gray-500">
							{#if recipe.prep_time_minutes || recipe.cook_time_minutes}
								<span>
									⏱️ {(recipe.prep_time_minutes || 0) + (recipe.cook_time_minutes || 0)} min
								</span>
							{/if}
							<span>👥 {recipe.servings}</span>
							<span class="px-2 py-0.5 rounded-full text-xs {difficultyColors[recipe.difficulty]}">
								{recipe.difficulty}
							</span>
						</div>
						{#if recipe.tags.length > 0}
							<div class="flex flex-wrap gap-1 mt-2">
								{#each recipe.tags as tag}
									<span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
										{tag.name}
									</span>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
