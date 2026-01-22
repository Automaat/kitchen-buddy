<script lang="ts">
	import { Card, CardContent, isMobile } from '@mskalski/home-ui';
	import type { RecipeListItem, Tag, DifficultyLevel, DietaryTag } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { onMount } from 'svelte';
	import { allDietaryTags, dietaryTagLabels } from '$lib/constants/dietary-tags';

	let recipes: RecipeListItem[] = $state([]);
	let tags: Tag[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let selectedDifficulty = $state<DifficultyLevel | ''>('');
	let selectedTagIds = $state<number[]>([]);
	let selectedDietaryTags = $state<DietaryTag[]>([]);
	let favoritesOnly = $state(false);

	async function loadRecipes() {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams();
			if (search) params.set('search', search);
			if (selectedDifficulty) params.set('difficulty', selectedDifficulty);
			if (selectedTagIds.length) params.set('tag_ids', selectedTagIds.join(','));
			if (selectedDietaryTags.length) {
				selectedDietaryTags.forEach((tag) => params.append('dietary_tags', tag));
			}
			if (favoritesOnly) params.set('favorites_only', 'true');

			recipes = await api.get<RecipeListItem[]>(`/recipes?${params}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load recipes';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		try {
			tags = await api.get<Tag[]>('/tags');
		} catch {
			/* ignore */
		}
		await loadRecipes();
	});

	async function toggleFavorite(recipe: RecipeListItem) {
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

	function toggleDietaryTag(tag: DietaryTag) {
		if (selectedDietaryTags.includes(tag)) {
			selectedDietaryTags = selectedDietaryTags.filter((t) => t !== tag);
		} else {
			selectedDietaryTags = [...selectedDietaryTags, tag];
		}
		loadRecipes();
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Recipes</h1>
		<a href="/recipes/new" class="btn btn-primary">Add Recipe</a>
	</div>

	<Card>
		<CardContent>
			<div class="filters">
				<div class="filter-row">
					<input
						type="text"
						placeholder="Search recipes..."
						bind:value={search}
						onchange={loadRecipes}
						class="input search-input"
					/>
					<select bind:value={selectedDifficulty} onchange={loadRecipes} class="input select">
						<option value="">All Difficulties</option>
						<option value="easy">Easy</option>
						<option value="medium">Medium</option>
						<option value="hard">Hard</option>
					</select>
					<label class="checkbox-label">
						<input type="checkbox" bind:checked={favoritesOnly} onchange={loadRecipes} />
						Favorites only
					</label>
				</div>
				{#if tags.length > 0}
					<div class="tag-row">
						{#each tags as tag}
							<button
								class="tag-btn tap-target"
								class:active={selectedTagIds.includes(tag.id)}
								onclick={() => {
									if (selectedTagIds.includes(tag.id)) {
										selectedTagIds = selectedTagIds.filter((id) => id !== tag.id);
									} else {
										selectedTagIds = [...selectedTagIds, tag.id];
									}
									loadRecipes();
								}}
							>
								{tag.name}
							</button>
						{/each}
					</div>
				{/if}
				<div class="tag-row">
					<span class="tag-label">Dietary:</span>
					{#each allDietaryTags as tag}
						<button
							class="tag-btn dietary tap-target"
							class:active={selectedDietaryTags.includes(tag)}
							onclick={() => toggleDietaryTag(tag)}
						>
							{dietaryTagLabels[tag]}
						</button>
					{/each}
				</div>
			</div>
		</CardContent>
	</Card>

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if error}
		<div class="error-message">{error}</div>
	{:else if recipes.length === 0}
		<div class="empty-state">
			No recipes found. <a href="/recipes/new" class="link">Add one!</a>
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
							<button onclick={() => toggleFavorite(recipe)} class="favorite-btn tap-target">
								{recipe.is_favorite ? '⭐' : '☆'}
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

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: var(--size-4);
		flex-wrap: wrap;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
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

	.filters {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.filter-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-4);
		align-items: center;
	}

	.input {
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
		flex: 1;
		min-width: 200px;
	}

	.select {
		min-width: 150px;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: var(--size-2);
		font-size: var(--font-size-1);
		cursor: pointer;
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-2);
		align-items: center;
	}

	.tag-label {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.tag-btn {
		padding: var(--size-1) var(--size-3);
		border-radius: 9999px;
		font-size: var(--font-size-0);
		border: none;
		cursor: pointer;
		background: var(--color-accent);
		color: var(--color-text);
		transition: all 0.2s;
	}

	.tag-btn:hover {
		background: var(--color-border);
	}

	.tag-btn.active {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.tag-btn.dietary.active {
		background: var(--color-success);
		color: var(--nord6);
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
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--size-4);
	}

	@media (min-width: 768px) {
		.recipe-grid {
			grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
			gap: var(--size-6);
		}
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
		line-clamp: 2;
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
