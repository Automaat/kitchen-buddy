<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
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

<div class="dashboard">
	<div class="page-header">
		<h1>Dashboard</h1>
	</div>

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if error}
		<div class="error-message">{error}</div>
	{:else if dashboard}
		<div class="kpi-grid">
			<Card>
				<CardHeader>
					<CardTitle>Recipes</CardTitle>
				</CardHeader>
				<CardContent>
					<div class="kpi-value primary">{dashboard.total_recipes}</div>
					<p class="kpi-subtitle">Total recipes</p>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Ingredients</CardTitle>
				</CardHeader>
				<CardContent>
					<div class="kpi-value success">{dashboard.total_ingredients}</div>
					<p class="kpi-subtitle">In database</p>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Favorites</CardTitle>
				</CardHeader>
				<CardContent>
					<div class="kpi-value warning">{dashboard.total_favorites}</div>
					<p class="kpi-subtitle">Starred recipes</p>
				</CardContent>
			</Card>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Today's Meals</CardTitle>
			</CardHeader>
			<CardContent>
				{#if dashboard.todays_meals.length === 0}
					<p class="empty-text">No meals planned for today.</p>
					<a href="/meal-planner" class="link">Plan your meals</a>
				{:else}
					<div class="meals-list">
						{#each dashboard.todays_meals as meal}
							<div class="meal-item">
								{#if meal.recipe.primary_image_id}
									<img
										src={getImageUrl(meal.recipe.primary_image_id)}
										alt={meal.recipe.title}
										class="meal-image"
									/>
								{:else}
									<div class="meal-image-placeholder">📷</div>
								{/if}
								<div class="meal-info">
									<div class="meal-type">{mealTypeLabels[meal.meal_type]}</div>
									<a href="/recipes/{meal.recipe.id}" class="meal-title">
										{meal.recipe.title}
									</a>
									<div class="meal-servings">{meal.servings} servings</div>
								</div>
								{#if meal.is_completed}
									<span class="completed-icon">✓</span>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</CardContent>
		</Card>
	{/if}
</div>

<style>
	.dashboard {
		display: flex;
		flex-direction: column;
		gap: var(--size-8);
	}

	.page-header h1 {
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

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: var(--size-6);
	}

	.kpi-value {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-7);
		margin-bottom: var(--size-2);
	}

	.kpi-value.primary {
		color: var(--color-primary);
	}

	.kpi-value.success {
		color: var(--color-success);
	}

	.kpi-value.warning {
		color: #ebcb8b;
	}

	.kpi-subtitle {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
		margin: 0;
	}

	.empty-text {
		color: var(--color-text-muted);
		margin: 0 0 var(--size-2) 0;
	}

	.link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
	}

	.meals-list {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.meal-item {
		display: flex;
		align-items: center;
		gap: var(--size-4);
		padding: var(--size-4);
		background: var(--color-bg-muted);
		border-radius: var(--radius-2);
	}

	.meal-image {
		width: 64px;
		height: 64px;
		object-fit: cover;
		border-radius: var(--radius-2);
	}

	.meal-image-placeholder {
		width: 64px;
		height: 64px;
		background: var(--color-accent);
		border-radius: var(--radius-2);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.meal-info {
		flex: 1;
	}

	.meal-type {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.meal-title {
		font-weight: var(--font-weight-6);
		color: var(--color-text);
		text-decoration: none;
	}

	.meal-title:hover {
		color: var(--color-primary);
	}

	.meal-servings {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.completed-icon {
		color: var(--color-success);
	}
</style>
