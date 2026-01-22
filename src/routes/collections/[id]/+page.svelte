<script lang="ts">
	import { Card, CardContent, Modal } from '@mskalski/home-ui';
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
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipes';
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
	<div class="loading">Loading...</div>
{:else if error}
	<div class="error-message">{error}</div>
{:else if collection}
	<div class="page">
		<div class="page-header">
			<div>
				<h1>{collection.name}</h1>
				{#if collection.description}
					<p class="description">{collection.description}</p>
				{/if}
				<p class="count">
					{collection.recipe_count} recipe{collection.recipe_count !== 1 ? 's' : ''}
				</p>
			</div>
			<div class="header-actions">
				<button onclick={openAddModal} class="btn btn-primary">Add Recipe</button>
				<button onclick={deleteCollection} class="btn btn-danger">Delete</button>
			</div>
		</div>

		{#if collection.recipes.length === 0}
			<div class="empty-state">
				No recipes in this collection yet. Add some recipes to get started!
			</div>
		{:else}
			<div class="recipe-grid">
				{#each collection.recipes as recipe}
					<Card>
						<a href="/recipes/{recipe.id}" class="recipe-image-link">
							{#if recipe.primary_image_id}
								<img
									src={getImageUrl(recipe.primary_image_id)}
									alt={recipe.title}
									class="recipe-image"
								/>
							{:else}
								<div class="recipe-image-placeholder">🍽️</div>
							{/if}
						</a>
						<CardContent>
							<div class="recipe-header">
								<a href="/recipes/{recipe.id}" class="recipe-title">{recipe.title}</a>
								<button onclick={() => removeRecipe(recipe.id)} class="remove-btn">Remove</button>
							</div>
						</CardContent>
					</Card>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<Modal
	open={showAddModal}
	title="Add Recipe to Collection"
	onCancel={() => {
		showAddModal = false;
		searchQuery = '';
	}}
	showActions={false}
>
	<input
		type="text"
		bind:value={searchQuery}
		placeholder="Search recipes..."
		class="input search-input"
	/>
	<div class="recipe-list">
		{#if filteredRecipes.length === 0}
			<p class="no-recipes">No recipes available to add.</p>
		{:else}
			{#each filteredRecipes as recipe}
				<button onclick={() => addRecipe(recipe.id)} class="recipe-item">
					{#if recipe.primary_image_id}
						<img
							src={getImageUrl(recipe.primary_image_id)}
							alt={recipe.title}
							class="recipe-item-image"
						/>
					{:else}
						<div class="recipe-item-placeholder">🍽️</div>
					{/if}
					<span class="recipe-item-title">{recipe.title}</span>
				</button>
			{/each}
		{/if}
	</div>
</Modal>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
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

	.count {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		margin: var(--size-1) 0 0 0;
	}

	.header-actions {
		display: flex;
		gap: var(--size-2);
	}

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		transition: all 0.2s;
		border: none;
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
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

	.empty-state {
		text-align: center;
		padding: var(--size-8) 0;
		color: var(--color-text-muted);
	}

	.recipe-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--size-6);
	}

	.recipe-image-link {
		display: block;
	}

	.recipe-image {
		width: 100%;
		height: 200px;
		object-fit: cover;
		border-radius: var(--radius-2) var(--radius-2) 0 0;
	}

	.recipe-image-placeholder {
		width: 100%;
		height: 200px;
		background: var(--color-accent);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: var(--font-size-6);
		border-radius: var(--radius-2) var(--radius-2) 0 0;
	}

	.recipe-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.recipe-title {
		font-size: var(--font-size-3);
		font-weight: var(--font-weight-6);
		color: var(--color-text);
		text-decoration: none;
	}

	.recipe-title:hover {
		color: var(--color-primary);
	}

	.remove-btn {
		padding: var(--size-1) var(--size-2);
		font-size: var(--font-size-0);
		background: none;
		border: none;
		color: var(--color-error);
		cursor: pointer;
	}

	.remove-btn:hover {
		background: rgba(191, 97, 106, 0.1);
		border-radius: var(--radius-2);
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

	.search-input {
		margin-bottom: var(--size-4);
	}

	.recipe-list {
		display: flex;
		flex-direction: column;
		gap: var(--size-2);
		max-height: 400px;
		overflow-y: auto;
	}

	.no-recipes {
		text-align: center;
		padding: var(--size-4);
		color: var(--color-text-muted);
	}

	.recipe-item {
		display: flex;
		align-items: center;
		gap: var(--size-3);
		padding: var(--size-3);
		background: var(--color-bg-muted);
		border-radius: var(--radius-2);
		border: none;
		cursor: pointer;
		text-align: left;
		transition: background 0.2s;
	}

	.recipe-item:hover {
		background: var(--color-accent);
	}

	.recipe-item-image {
		width: 48px;
		height: 48px;
		object-fit: cover;
		border-radius: var(--radius-2);
	}

	.recipe-item-placeholder {
		width: 48px;
		height: 48px;
		background: var(--color-accent);
		border-radius: var(--radius-2);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: var(--font-size-4);
	}

	.recipe-item-title {
		font-weight: var(--font-weight-6);
	}
</style>
