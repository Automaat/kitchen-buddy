<script lang="ts">
	import { Card, CardContent } from '@mskalski/home-ui';
	import type { RecipeSuggestion } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
	import { onMount } from 'svelte';

	let suggestions: RecipeSuggestion[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let minMatchPercentage = $state(50);

	async function loadSuggestions() {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams();
			params.set('min_match_percentage', String(minMatchPercentage / 100));
			params.set('limit', '20');
			const response = await api.get<{ suggestions: RecipeSuggestion[] }>(`/suggestions?${params}`);
			suggestions = response.suggestions;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load suggestions';
		} finally {
			loading = false;
		}
	}

	onMount(loadSuggestions);

	function getMatchClass(percentage: number): string {
		if (percentage >= 80) return 'match-high';
		if (percentage >= 60) return 'match-medium';
		return 'match-low';
	}
</script>

<div class="page">
	<div class="page-header">
		<div>
			<h1 class="page-title">What can I cook?</h1>
			<p class="page-subtitle">Recipes based on your pantry ingredients</p>
		</div>
		<a href="/pantry" class="btn btn-secondary">Manage Pantry</a>
	</div>

	<Card>
		<CardContent>
			<div class="filter-row">
				<label for="minMatch" class="filter-label">Minimum ingredient match:</label>
				<input
					id="minMatch"
					type="range"
					min="0"
					max="100"
					step="10"
					bind:value={minMatchPercentage}
					onchange={loadSuggestions}
					class="range-input"
				/>
				<span class="range-value">{minMatchPercentage}%</span>
			</div>
		</CardContent>
	</Card>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading suggestions...</div>
	{:else if suggestions.length === 0}
		<div class="empty-state">
			<p>No recipes match your current pantry ingredients at {minMatchPercentage}% threshold.</p>
			<div class="empty-actions">
				<a href="/pantry" class="link">Add more pantry items</a>
				<span class="divider">or</span>
				<button onclick={() => { minMatchPercentage = 30; loadSuggestions(); }} class="link-btn">
					Lower the threshold
				</button>
			</div>
		</div>
	{:else}
		<div class="suggestion-grid">
			{#each suggestions as suggestion}
				<a href="/recipes/{suggestion.recipe_id}" class="suggestion-card">
					<Card>
						{#if suggestion.primary_image_id}
							<img
								src={getImageUrl(suggestion.primary_image_id)}
								alt={suggestion.recipe_title}
								class="suggestion-image"
							/>
						{:else}
							<div class="suggestion-image-placeholder">🍽️</div>
						{/if}
						<CardContent>
							<div class="suggestion-header">
								<h3 class="suggestion-title">{suggestion.recipe_title}</h3>
								<span class="match-badge {getMatchClass(suggestion.match_percentage)}">
									{suggestion.match_percentage}%
								</span>
							</div>
							<p class="suggestion-meta">
								{suggestion.available_ingredients} of {suggestion.total_ingredients} ingredients available
							</p>
							{#if suggestion.missing_ingredients.length > 0}
								<div class="missing-section">
									<p class="missing-label">Missing:</p>
									<div class="missing-tags">
										{#each suggestion.missing_ingredients.slice(0, 3) as missing}
											<span class="missing-tag">{missing.ingredient_name}</span>
										{/each}
										{#if suggestion.missing_ingredients.length > 3}
											<span class="more-tag">+{suggestion.missing_ingredients.length - 3} more</span>
										{/if}
									</div>
								</div>
							{/if}
						</CardContent>
					</Card>
				</a>
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
		align-items: flex-start;
	}

	.page-title {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.page-subtitle {
		color: var(--color-text-muted);
		margin: var(--size-1) 0 0 0;
	}

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		transition: all 0.2s;
		border: 1px solid var(--color-border);
	}

	.btn-secondary {
		background: transparent;
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-accent);
	}

	.filter-row {
		display: flex;
		align-items: center;
		gap: var(--size-4);
	}

	.filter-label {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
	}

	.range-input {
		width: 200px;
	}

	.range-value {
		font-size: var(--font-size-1);
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

	.empty-state {
		text-align: center;
		padding: var(--size-8) 0;
		color: var(--color-text-muted);
	}

	.empty-actions {
		display: flex;
		gap: var(--size-4);
		justify-content: center;
		margin-top: var(--size-4);
	}

	.divider {
		color: var(--color-text-muted);
	}

	.link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.link:hover {
		text-decoration: underline;
	}

	.link-btn {
		background: none;
		border: none;
		color: var(--color-primary);
		cursor: pointer;
		font-size: inherit;
	}

	.link-btn:hover {
		text-decoration: underline;
	}

	.suggestion-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--size-6);
	}

	.suggestion-card {
		text-decoration: none;
		color: inherit;
		transition: transform 0.2s;
	}

	.suggestion-card:hover {
		transform: translateY(-2px);
	}

	.suggestion-image {
		width: 100%;
		height: 200px;
		object-fit: cover;
		border-radius: var(--radius-2) var(--radius-2) 0 0;
	}

	.suggestion-image-placeholder {
		width: 100%;
		height: 200px;
		background: var(--color-accent);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: var(--font-size-6);
		border-radius: var(--radius-2) var(--radius-2) 0 0;
	}

	.suggestion-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: var(--size-2);
	}

	.suggestion-title {
		font-size: var(--font-size-2);
		font-weight: var(--font-weight-6);
		margin: 0;
	}

	.match-badge {
		padding: var(--size-1) var(--size-2);
		border-radius: 9999px;
		font-size: var(--font-size-0);
		font-weight: var(--font-weight-6);
	}

	.match-badge.match-high {
		background: rgba(163, 190, 140, 0.2);
		color: var(--color-success);
	}

	.match-badge.match-medium {
		background: rgba(235, 203, 139, 0.2);
		color: #d08770;
	}

	.match-badge.match-low {
		background: rgba(208, 135, 112, 0.2);
		color: #bf616a;
	}

	.suggestion-meta {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
		margin: var(--size-2) 0 0 0;
	}

	.missing-section {
		margin-top: var(--size-3);
	}

	.missing-label {
		font-size: var(--font-size-0);
		font-weight: var(--font-weight-6);
		color: var(--color-text-muted);
		margin: 0 0 var(--size-1) 0;
	}

	.missing-tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-1);
	}

	.missing-tag {
		font-size: var(--font-size-0);
		padding: var(--size-1) var(--size-2);
		background: rgba(191, 97, 106, 0.1);
		color: var(--color-error);
		border-radius: var(--radius-2);
	}

	.more-tag {
		font-size: var(--font-size-0);
		padding: var(--size-1) var(--size-2);
		background: var(--color-accent);
		color: var(--color-text-muted);
		border-radius: var(--radius-2);
	}
</style>
