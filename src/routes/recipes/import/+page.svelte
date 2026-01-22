<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
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

<div class="page">
	<div class="page-header">
		<h1>Import Recipe from URL</h1>
		<a href="/recipes/new" class="btn btn-secondary">Manual Entry</a>
	</div>

	<Card>
		<CardContent>
			<p class="description">
				Paste a recipe URL below to import the recipe data. Works best with sites that use schema.org
				recipe markup (AllRecipes, Food Network, BBC Good Food, etc.).
			</p>

			<div class="import-form">
				<input
					type="url"
					bind:value={url}
					placeholder="https://example.com/recipe/chocolate-cake"
					class="input"
				/>
				<button onclick={handleImport} disabled={loading || !url.trim()} class="btn btn-primary">
					{loading ? 'Importing...' : 'Import'}
				</button>
			</div>

			{#if error}
				<div class="error-message">{error}</div>
			{/if}
		</CardContent>
	</Card>

	{#if importedData}
		<Card>
			<CardHeader>
				<CardTitle>Preview</CardTitle>
			</CardHeader>
			<CardContent>
				<div class="preview-grid">
					{#if importedData.image_url}
						<img src={importedData.image_url} alt={importedData.title || 'Recipe'} class="preview-image" />
					{/if}
					<div class="preview-info">
						<h3>{importedData.title || 'Untitled Recipe'}</h3>
						{#if importedData.description}
							<p class="preview-desc">{importedData.description}</p>
						{/if}
						<div class="preview-meta">
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
					<div class="preview-section">
						<h4>Ingredients ({importedData.ingredients.length})</h4>
						<ul class="ingredient-list">
							{#each importedData.ingredients as ingredient}
								<li>• {ingredient}</li>
							{/each}
						</ul>
					</div>
				{/if}

				{#if importedData.instructions}
					<div class="preview-section">
						<h4>Instructions</h4>
						<div class="instructions-preview">{importedData.instructions}</div>
					</div>
				{/if}

				<div class="notice">
					<strong>Note:</strong> Ingredients will need to be matched to your ingredient database after
					creating the recipe. You can do this on the edit page.
				</div>

				<div class="preview-actions">
					<button onclick={handleCreate} disabled={loading} class="btn btn-success">
						{loading ? 'Creating...' : 'Create Recipe'}
					</button>
					<button onclick={() => (importedData = null)} class="btn btn-secondary">Cancel</button>
				</div>
			</CardContent>
		</Card>
	{/if}
</div>

<style>
	.page {
		max-width: 800px;
		margin: 0 auto;
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

	.description {
		color: var(--color-text-muted);
		margin: 0 0 var(--size-4) 0;
	}

	.import-form {
		display: flex;
		gap: var(--size-2);
	}

	.import-form .input {
		flex: 1;
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

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		border: none;
		white-space: nowrap;
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: var(--color-accent);
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-border);
	}

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.btn-success:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.error-message {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
		padding: var(--size-4);
		border-radius: var(--radius-2);
		margin-top: var(--size-4);
	}

	.preview-grid {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: var(--size-4);
		margin-bottom: var(--size-4);
	}

	@media (max-width: 600px) {
		.preview-grid {
			grid-template-columns: 1fr;
		}
	}

	.preview-image {
		width: 200px;
		height: 150px;
		object-fit: cover;
		border-radius: var(--radius-2);
	}

	.preview-info h3 {
		font-size: var(--font-size-3);
		font-weight: var(--font-weight-6);
		margin: 0 0 var(--size-2) 0;
	}

	.preview-desc {
		color: var(--color-text-muted);
		font-size: var(--font-size-0);
		margin: 0 0 var(--size-2) 0;
	}

	.preview-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--size-4);
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.preview-section {
		margin-bottom: var(--size-4);
	}

	.preview-section h4 {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		margin: 0 0 var(--size-2) 0;
	}

	.ingredient-list {
		list-style: none;
		padding: 0;
		margin: 0;
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		max-height: 150px;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.instructions-preview {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		white-space: pre-wrap;
		max-height: 150px;
		overflow-y: auto;
	}

	.notice {
		background: rgba(235, 203, 139, 0.2);
		color: #d08770;
		padding: var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-0);
		margin-bottom: var(--size-4);
	}

	.preview-actions {
		display: flex;
		gap: var(--size-4);
	}
</style>
