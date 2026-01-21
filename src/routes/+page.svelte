<script lang="ts">
	import type { Dashboard } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { onMount } from 'svelte';

	let dashboard: Dashboard | null = $state(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			dashboard = await api.get<Dashboard>('/dashboard');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load dashboard';
		} finally {
			loading = false;
		}
	});

	const mealTypeLabels: Record<string, string> = {
		breakfast: 'Breakfast',
		lunch: 'Lunch',
		dinner: 'Dinner',
		snack: 'Snack'
	};
</script>

<div class="space-y-8">
	<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{:else if dashboard}
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<div class="text-3xl font-bold text-blue-600">{dashboard.total_recipes}</div>
				<div class="text-gray-600">Recipes</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<div class="text-3xl font-bold text-green-600">{dashboard.total_ingredients}</div>
				<div class="text-gray-600">Ingredients</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow-sm border">
				<div class="text-3xl font-bold text-yellow-600">{dashboard.total_favorites}</div>
				<div class="text-gray-600">Favorites</div>
			</div>
		</div>

		<div class="bg-white p-6 rounded-lg shadow-sm border">
			<h2 class="text-xl font-semibold mb-4">Today's Meals</h2>
			{#if dashboard.todays_meals.length === 0}
				<p class="text-gray-500">No meals planned for today.</p>
				<a href="/meal-planner" class="text-blue-600 hover:underline mt-2 inline-block">
					Plan your meals
				</a>
			{:else}
				<div class="space-y-4">
					{#each dashboard.todays_meals as meal}
						<div class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
							{#if meal.recipe.primary_image_id}
								<img
									src={getImageUrl(meal.recipe.primary_image_id)}
									alt={meal.recipe.title}
									class="w-16 h-16 object-cover rounded-lg"
								/>
							{:else}
								<div class="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
									📷
								</div>
							{/if}
							<div class="flex-1">
								<div class="text-sm text-gray-500">{mealTypeLabels[meal.meal_type]}</div>
								<a href="/recipes/{meal.recipe.id}" class="font-medium hover:text-blue-600">
									{meal.recipe.title}
								</a>
								<div class="text-sm text-gray-500">{meal.servings} servings</div>
							</div>
							{#if meal.is_completed}
								<span class="text-green-600">✓</span>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
