<script lang="ts">
	import { Card, CardContent, Modal } from '@mskalski/home-ui';
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

<div class="page">
	<div class="page-header">
		<h1>Meal Planner</h1>
		<div class="week-nav">
			<button onclick={prevWeek} class="nav-btn">←</button>
			<span class="week-range">
				{formatDate(currentWeekStart)} - {formatDate(addDays(currentWeekStart, 6))}
			</span>
			<button onclick={nextWeek} class="nav-btn">→</button>
		</div>
	</div>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading...</div>
	{:else}
		<div class="week-grid">
			{#each weekDays as day}
				<Card>
					<div class="day-header" class:today={toISODate(day) === toISODate(new Date())}>
						{formatDate(day)}
					</div>
					<CardContent>
						<div class="day-meals">
							{#each mealTypes as mealType}
								{@const meals = getMealsForDay(day).filter((m) => m.meal_type === mealType)}
								<div class="meal-section">
									<div class="meal-type-label">{mealTypeLabels[mealType]}</div>
									{#each meals as meal}
										<div class="meal-item" class:completed={meal.is_completed}>
											<button onclick={() => toggleComplete(meal)} class="check-btn">
												{meal.is_completed ? '✓' : '○'}
											</button>
											<a
												href="/recipes/{meal.recipe.id}"
												class="meal-title"
												class:done={meal.is_completed}
											>
												{meal.recipe.title}
											</a>
											<button onclick={() => deleteMealPlan(meal.id)} class="delete-btn">×</button>
										</div>
									{/each}
									<button onclick={() => openAddModal(day, mealType)} class="add-meal-btn">
										+ Add
									</button>
								</div>
							{/each}
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<Modal
	open={showAddModal}
	title="Add Meal"
	onCancel={() => (showAddModal = false)}
	onConfirm={addMealPlan}
	confirmText="Add"
	confirmDisabled={!selectedRecipeId}
>
	{#if recipes.length === 0}
		<p class="no-recipes">
			No recipes available.
			<a href="/recipes/new" class="link">Create one first.</a>
		</p>
	{:else}
		<div class="modal-form">
			<div class="form-group">
				<label for="recipe">Recipe</label>
				<select id="recipe" bind:value={selectedRecipeId} class="input">
					{#each recipes as recipe}
						<option value={recipe.id}>{recipe.title}</option>
					{/each}
				</select>
			</div>
			<div class="form-group">
				<label for="mealServings">Servings</label>
				<input id="mealServings" type="number" bind:value={servings} min="1" class="input" />
			</div>
		</div>
	{/if}
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
		align-items: center;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.week-nav {
		display: flex;
		align-items: center;
		gap: var(--size-4);
	}

	.nav-btn {
		padding: var(--size-2);
		background: none;
		border: none;
		cursor: pointer;
		font-size: var(--font-size-3);
		border-radius: var(--radius-2);
	}

	.nav-btn:hover {
		background: var(--color-accent);
	}

	.week-range {
		font-weight: var(--font-weight-6);
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

	.week-grid {
		display: grid;
		grid-template-columns: repeat(7, 1fr);
		gap: var(--size-2);
	}

	@media (max-width: 1200px) {
		.week-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	@media (max-width: 768px) {
		.week-grid {
			grid-template-columns: 1fr;
		}
	}

	.day-header {
		padding: var(--size-2) var(--size-3);
		background: var(--color-bg-muted);
		text-align: center;
		font-weight: var(--font-weight-6);
		border-bottom: 1px solid var(--color-border);
		border-radius: var(--radius-2) var(--radius-2) 0 0;
	}

	.day-header.today {
		background: rgba(136, 192, 208, 0.2);
		color: var(--color-primary);
	}

	.day-meals {
		display: flex;
		flex-direction: column;
		gap: var(--size-3);
		min-height: 200px;
	}

	.meal-section {
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.meal-type-label {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		font-weight: var(--font-weight-6);
	}

	.meal-item {
		display: flex;
		align-items: center;
		gap: var(--size-2);
		padding: var(--size-2);
		background: var(--color-bg-muted);
		border-radius: var(--radius-2);
		font-size: var(--font-size-0);
	}

	.meal-item.completed {
		opacity: 0.6;
	}

	.check-btn {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
	}

	.check-btn:hover {
		transform: scale(1.1);
	}

	.meal-title {
		flex: 1;
		text-decoration: none;
		color: var(--color-text);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.meal-title:hover {
		color: var(--color-primary);
	}

	.meal-title.done {
		text-decoration: line-through;
	}

	.delete-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-error);
		opacity: 0;
		transition: opacity 0.2s;
	}

	.meal-item:hover .delete-btn {
		opacity: 1;
	}

	.add-meal-btn {
		padding: var(--size-1);
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		background: none;
		border: none;
		cursor: pointer;
		text-align: center;
		border-radius: var(--radius-2);
	}

	.add-meal-btn:hover {
		background: var(--color-bg-muted);
		color: var(--color-text);
	}

	.modal-form {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: var(--size-2);
	}

	.form-group label {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
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

	.no-recipes {
		color: var(--color-text-muted);
	}

	.link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
	}
</style>
