<script lang="ts">
	import type { RecipeImportResponse } from '$lib/types';
	import { api } from '$lib/utils';
	import { goto } from '$app/navigation';

	let url = $state('');
	let loading = $state(false);
	let error = $state<string | null>(null);
	let importedData = $state<RecipeImportResponse | null>(null);

	async function handleImport() {
		if (!url.trim()) {
			error = 'URL is required';
			return;
		}

		loading = true;
		error = null;

		try {
			importedData = await api.post<RecipeImportResponse>('/recipes/import', { url });
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to import recipe';
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		if (!importedData) return;

		loading = true;
		error = null;

		try {
			const recipe = await api.post<{ id: number }>('/recipes', {
				title: importedData.title || 'Imported Recipe',
				description: importedData.description || null,
				instructions: importedData.instructions || null,
				prep_time_minutes: importedData.prep_time_minutes,
				cook_time_minutes: importedData.cook_time_minutes,
				servings: importedData.servings || 4,
				difficulty: 'medium',
				dietary_tags: [],
				source_url: importedData.source_url,
				tag_ids: [],
				ingredients: []
			});

			goto(`/recipes/${recipe.id}/edit`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create recipe';
		} finally {
			loading = false;
		}
	}
</script>

<div class="max-w-3xl mx-auto space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Import Recipe from URL</h1>
		<a href="/recipes/new" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
			Manual Entry
		</a>
	</div>

	<div class="bg-white p-6 rounded-lg shadow-sm border space-y-4">
		<p class="text-gray-600">
			Paste a recipe URL below to import the recipe data. Works best with sites that use schema.org
			recipe markup (AllRecipes, Food Network, BBC Good Food, etc.).
		</p>

		<div class="flex gap-2">
			<input
				type="url"
				bind:value={url}
				placeholder="https://example.com/recipe/chocolate-cake"
				class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
			/>
			<button
				onclick={handleImport}
				disabled={loading || !url.trim()}
				class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
			>
				{loading ? 'Importing...' : 'Import'}
			</button>
		</div>

		{#if error}
			<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
		{/if}
	</div>

	{#if importedData}
		<div class="bg-white p-6 rounded-lg shadow-sm border space-y-4">
			<h2 class="text-xl font-semibold">Preview</h2>

			<div class="grid md:grid-cols-2 gap-4">
				{#if importedData.image_url}
					<img
						src={importedData.image_url}
						alt={importedData.title || 'Recipe'}
						class="w-full h-48 object-cover rounded-lg"
					/>
				{/if}
				<div class="space-y-2">
					<h3 class="text-lg font-medium">{importedData.title || 'Untitled Recipe'}</h3>
					{#if importedData.description}
						<p class="text-gray-600 text-sm">{importedData.description}</p>
					{/if}
					<div class="flex flex-wrap gap-4 text-sm text-gray-500">
						{#if importedData.prep_time_minutes}
							<span>Prep: {importedData.prep_time_minutes} min</span>
						{/if}
						{#if importedData.cook_time_minutes}
							<span>Cook: {importedData.cook_time_minutes} min</span>
						{/if}
						{#if importedData.servings}
							<span>Servings: {importedData.servings}</span>
						{/if}
					</div>
				</div>
			</div>

			{#if importedData.ingredients.length > 0}
				<div>
					<h4 class="font-medium mb-2">Ingredients ({importedData.ingredients.length})</h4>
					<ul class="text-sm text-gray-600 space-y-1 max-h-40 overflow-y-auto">
						{#each importedData.ingredients as ingredient}
							<li>• {ingredient}</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if importedData.instructions}
				<div>
					<h4 class="font-medium mb-2">Instructions</h4>
					<div class="text-sm text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
						{importedData.instructions}
					</div>
				</div>
			{/if}

			<div class="bg-yellow-50 p-4 rounded-lg text-sm text-yellow-800">
				<strong>Note:</strong> Ingredients will need to be matched to your ingredient database after
				creating the recipe. You can do this on the edit page.
			</div>

			<div class="flex gap-4">
				<button
					onclick={handleCreate}
					disabled={loading}
					class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
				>
					{loading ? 'Creating...' : 'Create Recipe'}
				</button>
				<button
					onclick={() => (importedData = null)}
					class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
				>
					Cancel
				</button>
			</div>
		</div>
	{/if}
</div>
