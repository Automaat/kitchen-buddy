<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
	import type { Ingredient, IngredientCategory } from '$lib/types';
	import { api } from '$lib/utils';
	import { onMount } from 'svelte';

	let ingredients: Ingredient[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let showForm = $state(false);
	let editingId = $state<number | null>(null);

	let name = $state('');
	let category = $state<IngredientCategory>('other');
	let defaultUnit = $state('');
	let calories = $state('');
	let protein = $state('');
	let carbs = $state('');
	let fat = $state('');
	let fiber = $state('');
	let costPerUnit = $state('');

	const categories: IngredientCategory[] = [
		'produce', 'dairy', 'meat', 'seafood', 'pantry', 'frozen', 'bakery', 'beverages', 'condiments', 'spices', 'other'
	];

	async function loadIngredients() {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams();
			if (search) params.set('search', search);
			ingredients = await api.get<Ingredient[]>(`/ingredients?${params}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load ingredients';
		} finally {
			loading = false;
		}
	}

	onMount(loadIngredients);

	function resetForm() {
		name = '';
		category = 'other';
		defaultUnit = '';
		calories = '';
		protein = '';
		carbs = '';
		fat = '';
		fiber = '';
		costPerUnit = '';
		showForm = false;
		editingId = null;
	}

	function startEdit(ingredient: Ingredient) {
		name = ingredient.name;
		category = ingredient.category;
		defaultUnit = ingredient.default_unit || '';
		calories = ingredient.calories?.toString() || '';
		protein = ingredient.protein?.toString() || '';
		carbs = ingredient.carbs?.toString() || '';
		fat = ingredient.fat?.toString() || '';
		fiber = ingredient.fiber?.toString() || '';
		costPerUnit = ingredient.cost_per_unit?.toString() || '';
		editingId = ingredient.id;
		showForm = true;
	}

	async function handleSubmit() {
		if (!name.trim()) return;

		try {
			const data = {
				name: name.trim(),
				category,
				default_unit: defaultUnit.trim() || null,
				calories: calories ? parseFloat(calories) : null,
				protein: protein ? parseFloat(protein) : null,
				carbs: carbs ? parseFloat(carbs) : null,
				fat: fat ? parseFloat(fat) : null,
				fiber: fiber ? parseFloat(fiber) : null,
				cost_per_unit: costPerUnit ? parseFloat(costPerUnit) : null
			};

			if (editingId) {
				await api.put(`/ingredients/${editingId}`, data);
			} else {
				await api.post('/ingredients', data);
			}

			resetForm();
			await loadIngredients();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save ingredient';
		}
	}

	async function deleteIngredient(id: number) {
		if (!confirm('Delete this ingredient?')) return;
		try {
			await api.delete(`/ingredients/${id}`);
			await loadIngredients();
		} catch {
			/* ignore */
		}
	}

	function getCategoryClass(cat: IngredientCategory): string {
		const classes: Record<IngredientCategory, string> = {
			produce: 'cat-produce',
			dairy: 'cat-dairy',
			meat: 'cat-meat',
			seafood: 'cat-seafood',
			pantry: 'cat-pantry',
			frozen: 'cat-frozen',
			bakery: 'cat-bakery',
			beverages: 'cat-beverages',
			condiments: 'cat-condiments',
			spices: 'cat-spices',
			other: 'cat-other'
		};
		return classes[cat];
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Ingredients</h1>
		<button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary">Add Ingredient</button>
	</div>

	{#if showForm}
		<Card>
			<CardHeader>
				<CardTitle>{editingId ? 'Edit Ingredient' : 'New Ingredient'}</CardTitle>
			</CardHeader>
			<CardContent>
				<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="form">
					<div class="form-grid-3">
						<div class="form-group">
							<label for="name">Name *</label>
							<input id="name" type="text" bind:value={name} required class="input" />
						</div>
						<div class="form-group">
							<label for="category">Category</label>
							<select id="category" bind:value={category} class="input">
								{#each categories as cat}
									<option value={cat}>{cat}</option>
								{/each}
							</select>
						</div>
						<div class="form-group">
							<label for="unit">Default Unit</label>
							<input id="unit" type="text" bind:value={defaultUnit} placeholder="g, ml, pcs..." class="input" />
						</div>
					</div>

					<div class="section-divider">
						<h3>Nutrition Info (per 100g)</h3>
						<div class="form-grid-5">
							<div class="form-group">
								<label for="calories">Calories</label>
								<input id="calories" type="number" step="0.1" bind:value={calories} placeholder="kcal" class="input input-sm" />
							</div>
							<div class="form-group">
								<label for="protein">Protein (g)</label>
								<input id="protein" type="number" step="0.1" bind:value={protein} class="input input-sm" />
							</div>
							<div class="form-group">
								<label for="carbs">Carbs (g)</label>
								<input id="carbs" type="number" step="0.1" bind:value={carbs} class="input input-sm" />
							</div>
							<div class="form-group">
								<label for="fat">Fat (g)</label>
								<input id="fat" type="number" step="0.1" bind:value={fat} class="input input-sm" />
							</div>
							<div class="form-group">
								<label for="fiber">Fiber (g)</label>
								<input id="fiber" type="number" step="0.1" bind:value={fiber} class="input input-sm" />
							</div>
						</div>
					</div>

					<div class="section-divider">
						<h3>Cost Info</h3>
						<div class="form-group" style="max-width: 200px;">
							<label for="costPerUnit">Cost per unit ($/100g)</label>
							<input id="costPerUnit" type="number" step="0.01" bind:value={costPerUnit} placeholder="0.00" class="input input-sm" />
						</div>
					</div>

					<div class="form-actions">
						<button type="submit" class="btn btn-primary">{editingId ? 'Update' : 'Add'}</button>
						<button type="button" onclick={resetForm} class="btn btn-secondary">Cancel</button>
					</div>
				</form>
			</CardContent>
		</Card>
	{/if}

	<Card>
		<CardContent>
			<input
				type="text"
				placeholder="Search ingredients..."
				bind:value={search}
				oninput={loadIngredients}
				class="input"
			/>
		</CardContent>
	</Card>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if ingredients.length === 0}
		<div class="empty-state">No ingredients found. Add some to get started!</div>
	{:else}
		<Card>
			<CardContent>
				<div class="table-container">
					<table class="table">
						<thead>
							<tr>
								<th>Name</th>
								<th>Category</th>
								<th>Unit</th>
								<th>Cal</th>
								<th>P/C/F</th>
								<th>Cost</th>
								<th class="actions-col">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each ingredients as ingredient}
								<tr>
									<td class="name-cell">{ingredient.name}</td>
									<td>
										<span class="category-badge {getCategoryClass(ingredient.category)}">
											{ingredient.category}
										</span>
									</td>
									<td class="muted">{ingredient.default_unit || '-'}</td>
									<td class="muted">{ingredient.calories ? `${ingredient.calories}` : '-'}</td>
									<td class="muted">
										{ingredient.protein || ingredient.carbs || ingredient.fat
											? `${ingredient.protein || 0}/${ingredient.carbs || 0}/${ingredient.fat || 0}g`
											: '-'}
									</td>
									<td class="muted">{ingredient.cost_per_unit ? `$${ingredient.cost_per_unit}` : '-'}</td>
									<td class="actions-col">
										<button onclick={() => startEdit(ingredient)} class="link-btn">Edit</button>
										<button onclick={() => deleteIngredient(ingredient.id)} class="link-btn danger">Delete</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</CardContent>
		</Card>
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
		border: none;
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
	}

	.btn-secondary {
		background: var(--color-accent);
		color: var(--color-text);
	}

	.btn-secondary:hover {
		background: var(--color-border);
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-grid-3 {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--size-4);
	}

	.form-grid-5 {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: var(--size-4);
	}

	@media (max-width: 768px) {
		.form-grid-3, .form-grid-5 {
			grid-template-columns: 1fr 1fr;
		}
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: var(--size-1);
	}

	.form-group label {
		font-size: var(--font-size-0);
		font-weight: var(--font-weight-6);
	}

	.section-divider {
		padding-top: var(--size-4);
		border-top: 1px solid var(--color-border);
	}

	.section-divider h3 {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		margin: 0 0 var(--size-3) 0;
	}

	.form-actions {
		display: flex;
		gap: var(--size-2);
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

	.input-sm {
		padding: var(--size-2) var(--size-3);
		font-size: var(--font-size-0);
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

	.table-container {
		overflow-x: auto;
	}

	.table {
		width: 100%;
		border-collapse: collapse;
	}

	.table th {
		text-align: left;
		padding: var(--size-3) var(--size-4);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		background: var(--color-bg-muted);
		border-bottom: 1px solid var(--color-border);
	}

	.table td {
		padding: var(--size-3) var(--size-4);
		font-size: var(--font-size-1);
		border-bottom: 1px solid var(--color-border);
	}

	.table tbody tr:hover {
		background: var(--color-bg-muted);
	}

	.name-cell {
		font-weight: var(--font-weight-6);
	}

	.muted {
		color: var(--color-text-muted);
	}

	.actions-col {
		text-align: right;
	}

	.category-badge {
		padding: var(--size-1) var(--size-2);
		border-radius: 9999px;
		font-size: var(--font-size-0);
	}

	.cat-produce { background: rgba(163, 190, 140, 0.2); color: #a3be8c; }
	.cat-dairy { background: rgba(129, 161, 193, 0.2); color: #81a1c1; }
	.cat-meat { background: rgba(191, 97, 106, 0.2); color: #bf616a; }
	.cat-seafood { background: rgba(136, 192, 208, 0.2); color: #88c0d0; }
	.cat-pantry { background: rgba(235, 203, 139, 0.2); color: #ebcb8b; }
	.cat-frozen { background: rgba(180, 142, 173, 0.2); color: #b48ead; }
	.cat-bakery { background: rgba(208, 135, 112, 0.2); color: #d08770; }
	.cat-beverages { background: rgba(180, 142, 173, 0.2); color: #b48ead; }
	.cat-condiments { background: rgba(235, 203, 139, 0.2); color: #ebcb8b; }
	.cat-spices { background: rgba(208, 135, 112, 0.2); color: #d08770; }
	.cat-other { background: var(--color-accent); color: var(--color-text-muted); }

	.link-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-primary);
		font-size: var(--font-size-1);
		margin-right: var(--size-2);
	}

	.link-btn:hover {
		text-decoration: underline;
	}

	.link-btn.danger {
		color: var(--color-error);
		margin-right: 0;
	}
</style>
