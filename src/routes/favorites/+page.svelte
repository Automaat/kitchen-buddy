<script lang="ts">
	import { Card, CardContent } from '@mskalski/home-ui';
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
</script>

<div class="page">
	<h1 class="page-title">Favorites</h1>

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if error}
		<div class="error-message">{error}</div>
	{:else if recipes.length === 0}
		<div class="empty-state">
			No favorite recipes yet.
			<a href="/recipes" class="link">Browse recipes</a>
			and mark some as favorites!
		</div>
	{:else}
		<div class="recipe-grid">
			{#each recipes as recipe}
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
							<button
								onclick={() => removeFavorite(recipe)}
								class="favorite-btn"
								title="Remove from favorites"
							>
								⭐
							</button>
						</div>
						{#if recipe.description}
							<p class="recipe-description">{recipe.description}</p>
						{/if}
						<div class="recipe-meta">
							{#if recipe.prep_time_minutes || recipe.cook_time_minutes}
								<span>⏱️ {(recipe.prep_time_minutes || 0) + (recipe.cook_time_minutes || 0)} min</span>
							{/if}
							<span>👥 {recipe.servings}</span>
							<span class="difficulty-badge {recipe.difficulty}">{recipe.difficulty}</span>
						</div>
						{#if recipe.tags.length > 0}
							<div class="recipe-tags">
								{#each recipe.tags as tag}
									<span class="tag">{tag.name}</span>
								{/each}
							</div>
						{/if}
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-title {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
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

	.link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
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
		align-items: flex-start;
		gap: var(--size-2);
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

	.favorite-btn {
		background: none;
		border: none;
		font-size: var(--font-size-4);
		cursor: pointer;
		transition: transform 0.2s;
	}

	.favorite-btn:hover {
		transform: scale(1.1);
	}

	.recipe-description {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
		margin: var(--size-2) 0;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.recipe-meta {
		display: flex;
		gap: var(--size-3);
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		margin-top: var(--size-3);
		align-items: center;
	}

	.difficulty-badge {
		padding: var(--size-1) var(--size-2);
		border-radius: 9999px;
		font-size: var(--font-size-0);
	}

	.difficulty-badge.easy {
		background: rgba(163, 190, 140, 0.2);
		color: var(--color-success);
	}

	.difficulty-badge.medium {
		background: rgba(235, 203, 139, 0.2);
		color: #d08770;
	}

	.difficulty-badge.hard {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
	}

	.recipe-tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-1);
		margin-top: var(--size-2);
	}

	.tag {
		padding: var(--size-1) var(--size-2);
		background: var(--color-accent);
		color: var(--color-text-muted);
		border-radius: 9999px;
		font-size: var(--font-size-0);
	}
</style>
