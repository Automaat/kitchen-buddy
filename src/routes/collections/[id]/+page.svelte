<script lang="ts">
	import type { CollectionDetail, RecipeListItem } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let collection: CollectionDetail | null = $state(null);
	let allRecipes: RecipeListItem[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showAddModal = $state(false);
	let searchQuery = $state('');

	const filteredRecipes = $derived(
		allRecipes.filter(
			(r) =>
				!collection?.recipes.some((cr) => cr.id === r.id) &&
				r.title.toLowerCase().includes(searchQuery.toLowerCase())
		)
	);

	onMount(async () => {
		await loadCollection();
	});

	async function loadCollection() {
		loading = true;
		error = null;
		try {
			collection = await api.get<CollectionDetail>(`/collections/${$page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load collection';
		} finally {
			loading = false;
		}
	}

	async function openAddModal() {
		try {
			allRecipes = await api.get<RecipeListItem[]>('/recipes');
			showAddModal = true;
		} catch {
			/* ignore */
		}
	}

	async function addRecipe(recipeId: number) {
		if (!collection) return;
		try {
			await api.post(`/collections/${collection.id}/recipes/${recipeId}`);
			await loadCollection();
			showAddModal = false;
			searchQuery = '';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add recipe';
		}
	}

	async function removeRecipe(recipeId: number) {
		if (!collection || !confirm('Remove this recipe from the collection?')) return;
		try {
			await api.delete(`/collections/${collection.id}/recipes/${recipeId}`);
			await loadCollection();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to remove recipe';
		}
	}

	async function deleteCollection() {
		if (!collection || !confirm('Delete this collection? Recipes will not be deleted.')) return;
		try {
			await api.delete(`/collections/${collection.id}`);
			goto('/collections');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete collection';
		}
	}
</script>

{#if loading}
	<div class="text-center py-12">Loading...</div>
{:else if error}
	<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
{:else if collection}
	<div class="space-y-6">
		<div class="flex items-start justify-between">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">{collection.name}</h1>
				{#if collection.description}
					<p class="text-gray-600 mt-2">{collection.description}</p>
				{/if}
				<p class="text-gray-500 text-sm mt-1">
					{collection.recipe_count} recipe{collection.recipe_count !== 1 ? 's' : ''}
				</p>
			</div>
			<div class="flex gap-2">
				<button
					onclick={openAddModal}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
				>
					Add Recipe
				</button>
				<button
					onclick={deleteCollection}
					class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
				>
					Delete
				</button>
			</div>
		</div>

		{#if collection.recipes.length === 0}
			<div class="text-center py-12 text-gray-500">
				No recipes in this collection yet. Add some recipes to get started!
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each collection.recipes as recipe}
					<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
						<a href="/recipes/{recipe.id}">
							{#if recipe.primary_image_id}
								<img
									src={getImageUrl(recipe.primary_image_id)}
									alt={recipe.title}
									class="w-full h-48 object-cover"
								/>
							{:else}
								<div
									class="w-full h-48 bg-gray-100 flex items-center justify-center text-4xl"
								>
									🍽️
								</div>
							{/if}
						</a>
						<div class="p-4">
							<a href="/recipes/{recipe.id}" class="font-semibold text-lg hover:text-blue-600">
								{recipe.title}
							</a>
							<button
								onclick={() => removeRecipe(recipe.id)}
								class="float-right px-2 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
							>
								Remove
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}

{#if showAddModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg p-6 w-full max-w-lg max-h-[80vh] flex flex-col">
			<h2 class="text-xl font-semibold mb-4">Add Recipe to Collection</h2>
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Search recipes..."
				class="w-full px-4 py-2 border rounded-lg mb-4"
			/>
			<div class="flex-1 overflow-y-auto space-y-2">
				{#if filteredRecipes.length === 0}
					<p class="text-gray-500 text-center py-4">No recipes available to add.</p>
				{:else}
					{#each filteredRecipes as recipe}
						<button
							onclick={() => addRecipe(recipe.id)}
							class="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 text-left"
						>
							{#if recipe.primary_image_id}
								<img
									src={getImageUrl(recipe.primary_image_id)}
									alt={recipe.title}
									class="w-12 h-12 object-cover rounded"
								/>
							{:else}
								<div
									class="w-12 h-12 bg-gray-200 rounded flex items-center justify-center text-xl"
								>
									🍽️
								</div>
							{/if}
							<span class="font-medium">{recipe.title}</span>
						</button>
					{/each}
				{/if}
			</div>
			<button
				onclick={() => {
					showAddModal = false;
					searchQuery = '';
				}}
				class="mt-4 px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
			>
				Close
			</button>
		</div>
	</div>
{/if}
