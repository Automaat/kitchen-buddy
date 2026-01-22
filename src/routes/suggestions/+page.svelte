<script lang="ts">
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
			const response = await api.get<{ suggestions: RecipeSuggestion[] }>(
				`/suggestions?${params}`
			);
			suggestions = response.suggestions;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load suggestions';
		} finally {
			loading = false;
		}
	}

	onMount(loadSuggestions);

	function getMatchColor(percentage: number): string {
		if (percentage >= 80) return 'bg-green-100 text-green-800';
		if (percentage >= 60) return 'bg-yellow-100 text-yellow-800';
		return 'bg-orange-100 text-orange-800';
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">What can I cook?</h1>
			<p class="text-gray-600 mt-1">Recipes based on your pantry ingredients</p>
		</div>
		<a href="/pantry" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
			Manage Pantry
		</a>
	</div>

	<div class="bg-white p-4 rounded-lg shadow-sm border">
		<div class="flex items-center gap-4">
			<label for="minMatch" class="text-sm font-medium text-gray-700">
				Minimum ingredient match:
			</label>
			<input
				id="minMatch"
				type="range"
				min="0"
				max="100"
				step="10"
				bind:value={minMatchPercentage}
				onchange={loadSuggestions}
				class="w-48"
			/>
			<span class="text-sm font-medium text-gray-900">{minMatchPercentage}%</span>
		</div>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading suggestions...</div>
	{:else if suggestions.length === 0}
		<div class="text-center py-12">
			<div class="text-gray-500 mb-4">
				No recipes match your current pantry ingredients at {minMatchPercentage}% threshold.
			</div>
			<div class="flex gap-4 justify-center">
				<a href="/pantry" class="text-blue-600 hover:underline">Add more pantry items</a>
				<span class="text-gray-400">or</span>
				<button onclick={() => { minMatchPercentage = 30; loadSuggestions(); }} class="text-blue-600 hover:underline">
					Lower the threshold
				</button>
			</div>
		</div>
	{:else}
		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each suggestions as suggestion}
				<a
					href="/recipes/{suggestion.recipe_id}"
					class="bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow"
				>
					{#if suggestion.primary_image_id}
						<img
							src={getImageUrl(suggestion.primary_image_id)}
							alt={suggestion.recipe_title}
							class="w-full h-48 object-cover"
						/>
					{:else}
						<div class="w-full h-48 bg-gray-100 flex items-center justify-center">
							<span class="text-4xl">🍽️</span>
						</div>
					{/if}
					<div class="p-4">
						<div class="flex items-start justify-between gap-2">
							<h3 class="font-semibold text-gray-900">{suggestion.recipe_title}</h3>
							<span
								class="px-2 py-0.5 rounded-full text-xs font-medium {getMatchColor(
									suggestion.match_percentage
								)}"
							>
								{suggestion.match_percentage}%
							</span>
						</div>
						<p class="text-sm text-gray-600 mt-2">
							{suggestion.available_ingredients} of {suggestion.total_ingredients} ingredients available
						</p>
						{#if suggestion.missing_ingredients.length > 0}
							<div class="mt-3">
								<p class="text-xs font-medium text-gray-500 mb-1">Missing:</p>
								<div class="flex flex-wrap gap-1">
									{#each suggestion.missing_ingredients.slice(0, 3) as missing}
										<span class="text-xs px-2 py-0.5 bg-red-50 text-red-700 rounded">
											{missing.ingredient_name}
										</span>
									{/each}
									{#if suggestion.missing_ingredients.length > 3}
										<span class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
											+{suggestion.missing_ingredients.length - 3} more
										</span>
									{/if}
								</div>
							</div>
						{/if}
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
