<script lang="ts">
	import type { WeekMealPlan, MealPlan, RecipeListItem, MealType } from '$lib/types';
	import { api, getImageUrl, toISODate, getWeekStart, getWeekDays, addDays, formatDate } from '$lib/utils';
	import { onMount } from 'svelte';

	let weekPlan: WeekMealPlan | null = $state(null);
	let recipes: RecipeListItem[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let currentWeekStart = $state(getWeekStart(new Date()));
	let weekDays = $derived(getWeekDays(currentWeekStart));

	let showAddModal = $state(false);
	let selectedDate = $state<Date | null>(null);
	let selectedMealType = $state<MealType>('dinner');
	let selectedRecipeId = $state<number | null>(null);
	let servings = $state(4);

	const mealTypes: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack'];
	const mealTypeLabels: Record<MealType, string> = {
		breakfast: 'Breakfast',
		lunch: 'Lunch',
		dinner: 'Dinner',
		snack: 'Snack'
	};

	async function loadWeek() {
		loading = true;
		error = null;
		try {
			weekPlan = await api.get<WeekMealPlan>(`/meal-plans/week/${toISODate(currentWeekStart)}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load meal plan';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		try {
			recipes = await api.get<RecipeListItem[]>('/recipes');
		} catch {
			/* ignore */
		}
		await loadWeek();
	});

	function prevWeek() {
		currentWeekStart = addDays(currentWeekStart, -7);
		loadWeek();
	}

	function nextWeek() {
		currentWeekStart = addDays(currentWeekStart, 7);
		loadWeek();
	}

	function getMealsForDay(date: Date): MealPlan[] {
		if (!weekPlan) return [];
		const dateStr = toISODate(date);
		return weekPlan.meals.filter((m) => m.date === dateStr);
	}

	function openAddModal(date: Date, mealType: MealType) {
		selectedDate = date;
		selectedMealType = mealType;
		selectedRecipeId = recipes[0]?.id || null;
		servings = 4;
		showAddModal = true;
	}

	async function addMealPlan() {
		if (!selectedDate || !selectedRecipeId) return;

		try {
			await api.post('/meal-plans', {
				date: toISODate(selectedDate),
				meal_type: selectedMealType,
				recipe_id: selectedRecipeId,
				servings
			});
			showAddModal = false;
			await loadWeek();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add meal';
		}
	}

	async function deleteMealPlan(id: number) {
		try {
			await api.delete(`/meal-plans/${id}`);
			await loadWeek();
		} catch {
			/* ignore */
		}
	}

	async function toggleComplete(meal: MealPlan) {
		try {
			await api.put(`/meal-plans/${meal.id}`, { is_completed: !meal.is_completed });
			meal.is_completed = !meal.is_completed;
		} catch {
			/* ignore */
		}
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Meal Planner</h1>
		<div class="flex items-center gap-4">
			<button onclick={prevWeek} class="p-2 hover:bg-gray-100 rounded-lg">←</button>
			<span class="font-medium">
				{formatDate(currentWeekStart)} - {formatDate(addDays(currentWeekStart, 6))}
			</span>
			<button onclick={nextWeek} class="p-2 hover:bg-gray-100 rounded-lg">→</button>
		</div>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else}
		<div class="grid grid-cols-7 gap-2">
			{#each weekDays as day}
				<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
					<div
						class="px-3 py-2 bg-gray-50 border-b text-center font-medium {toISODate(day) ===
						toISODate(new Date())
							? 'bg-blue-50 text-blue-700'
							: ''}"
					>
						{formatDate(day)}
					</div>
					<div class="p-2 space-y-2 min-h-[200px]">
						{#each mealTypes as mealType}
							{@const meals = getMealsForDay(day).filter((m) => m.meal_type === mealType)}
							<div class="text-xs text-gray-500 font-medium">{mealTypeLabels[mealType]}</div>
							{#each meals as meal}
								<div
									class="p-2 bg-gray-50 rounded text-sm group relative {meal.is_completed
										? 'opacity-60'
										: ''}"
								>
									<div class="flex items-center gap-2">
										<button onclick={() => toggleComplete(meal)} class="hover:scale-110">
											{meal.is_completed ? '✓' : '○'}
										</button>
										<a
											href="/recipes/{meal.recipe.id}"
											class="flex-1 truncate hover:text-blue-600 {meal.is_completed
												? 'line-through'
												: ''}"
										>
											{meal.recipe.title}
										</a>
										<button
											onclick={() => deleteMealPlan(meal.id)}
											class="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700"
										>
											×
										</button>
									</div>
								</div>
							{/each}
							<button
								onclick={() => openAddModal(day, mealType)}
								class="w-full p-1 text-xs text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
							>
								+ Add
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showAddModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
			<h2 class="text-xl font-semibold mb-4">Add Meal</h2>
			{#if recipes.length === 0}
				<p class="text-gray-500 mb-4">
					No recipes available.
					<a href="/recipes/new" class="text-blue-600 hover:underline">Create one first.</a>
				</p>
			{:else}
				<form onsubmit={(e) => { e.preventDefault(); addMealPlan(); }} class="space-y-4">
					<div>
						<label for="recipe" class="block text-sm font-medium text-gray-700 mb-1">Recipe</label>
						<select
							id="recipe"
							bind:value={selectedRecipeId}
							class="w-full px-4 py-2 border rounded-lg"
						>
							{#each recipes as recipe}
								<option value={recipe.id}>{recipe.title}</option>
							{/each}
						</select>
					</div>
					<div>
						<label for="mealServings" class="block text-sm font-medium text-gray-700 mb-1">
							Servings
						</label>
						<input
							id="mealServings"
							type="number"
							bind:value={servings}
							min="1"
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div class="flex gap-2">
						<button
							type="submit"
							class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
						>
							Add
						</button>
						<button
							type="button"
							onclick={() => (showAddModal = false)}
							class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
						>
							Cancel
						</button>
					</div>
				</form>
			{/if}
		</div>
	</div>
{/if}
