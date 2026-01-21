<script lang="ts">
	import type { RecipeListItem, Tag, DifficultyLevel, DietaryTag } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { onMount } from 'svelte';

	let recipes: RecipeListItem[] = $state([]);
	let tags: Tag[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let selectedDifficulty = $state<DifficultyLevel | ''>('');
	let selectedTagIds = $state<number[]>([]);
	let selectedDietaryTags = $state<DietaryTag[]>([]);
	let favoritesOnly = $state(false);

	const allDietaryTags: DietaryTag[] = [
		'vegetarian',
		'vegan',
		'gluten_free',
		'dairy_free',
		'nut_free',
		'low_carb',
		'keto',
		'paleo'
	];

	const dietaryTagLabels: Record<DietaryTag, string> = {
		vegetarian: 'Vegetarian',
		vegan: 'Vegan',
		gluten_free: 'Gluten-Free',
		dairy_free: 'Dairy-Free',
		nut_free: 'Nut-Free',
		low_carb: 'Low-Carb',
		keto: 'Keto',
		paleo: 'Paleo'
	};

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

	const difficultyColors: Record<DifficultyLevel, string> = {
		easy: 'bg-green-100 text-green-800',
		medium: 'bg-yellow-100 text-yellow-800',
		hard: 'bg-red-100 text-red-800'
	};
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Recipes</h1>
		<a
			href="/recipes/new"
			class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
		>
			Add Recipe
		</a>
	</div>

	<div class="bg-white p-4 rounded-lg shadow-sm border space-y-4">
		<div class="flex flex-wrap gap-4">
			<input
				type="text"
				placeholder="Search recipes..."
				bind:value={search}
				onchange={loadRecipes}
				class="flex-1 min-w-[200px] px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
			<select
				bind:value={selectedDifficulty}
				onchange={loadRecipes}
				class="px-4 py-2 border rounded-lg"
			>
				<option value="">All Difficulties</option>
				<option value="easy">Easy</option>
				<option value="medium">Medium</option>
				<option value="hard">Hard</option>
			</select>
			<label class="flex items-center gap-2">
				<input type="checkbox" bind:checked={favoritesOnly} onchange={loadRecipes} />
				Favorites only
			</label>
		</div>
		{#if tags.length > 0}
			<div class="flex flex-wrap gap-2">
				{#each tags as tag}
					<button
						class="px-3 py-1 rounded-full text-sm {selectedTagIds.includes(tag.id)
							? 'bg-blue-600 text-white'
							: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
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
		<div class="flex flex-wrap gap-2">
			<span class="text-sm text-gray-500 self-center">Dietary:</span>
			{#each allDietaryTags as tag}
				<button
					class="px-3 py-1 rounded-full text-sm {selectedDietaryTags.includes(tag)
						? 'bg-green-600 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
					onclick={() => toggleDietaryTag(tag)}
				>
					{dietaryTagLabels[tag]}
				</button>
			{/each}
		</div>
	</div>

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{:else if recipes.length === 0}
		<div class="text-center py-12 text-gray-500">
			No recipes found. <a href="/recipes/new" class="text-blue-600 hover:underline">Add one!</a>
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
								onclick={() => toggleFavorite(recipe)}
								class="text-xl hover:scale-110 transition-transform"
							>
								{recipe.is_favorite ? '⭐' : '☆'}
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
