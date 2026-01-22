<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent } from '@mskalski/home-ui';
	import type { PantryItem, Ingredient, IngredientCategory } from '$lib/types';
	import { api } from '$lib/utils';
	import { onMount } from 'svelte';

	let pantryItems: PantryItem[] = $state([]);
	let ingredients: Ingredient[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let showForm = $state(false);
	let editingId = $state<number | null>(null);

	let selectedIngredientId = $state<number | null>(null);
	let quantity = $state('');
	let unit = $state('');
	let expirationDate = $state('');
	let notes = $state('');

	async function loadPantryItems() {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams();
			if (search) params.set('search', search);
			pantryItems = await api.get<PantryItem[]>(`/pantry?${params}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load pantry';
		} finally {
			loading = false;
		}
	}

	async function loadIngredients() {
		try {
			ingredients = await api.get<Ingredient[]>('/ingredients');
		} catch {
			/* ignore */
		}
	}

	onMount(() => {
		loadPantryItems();
		loadIngredients();
	});

	function resetForm() {
		selectedIngredientId = null;
		quantity = '';
		unit = '';
		expirationDate = '';
		notes = '';
		showForm = false;
		editingId = null;
	}

	function startEdit(item: PantryItem) {
		selectedIngredientId = item.ingredient_id;
		quantity = String(item.quantity);
		unit = item.unit || '';
		expirationDate = item.expiration_date || '';
		notes = item.notes || '';
		editingId = item.id;
		showForm = true;
	}

	async function handleSubmit() {
		if (!selectedIngredientId || !quantity) return;

		try {
			const data = {
				ingredient_id: selectedIngredientId,
				quantity: parseFloat(quantity),
				unit: unit.trim() || null,
				expiration_date: expirationDate || null,
				notes: notes.trim() || null
			};

			if (editingId) {
				await api.put(`/pantry/${editingId}`, data);
			} else {
				await api.post('/pantry', data);
			}

			resetForm();
			await loadPantryItems();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save pantry item';
		}
	}

	async function deleteItem(id: number) {
		if (!confirm('Remove this item from pantry?')) return;
		try {
			await api.delete(`/pantry/${id}`);
			await loadPantryItems();
		} catch {
			/* ignore */
		}
	}

	function isExpiringSoon(date: string | null): boolean {
		if (!date) return false;
		const expDate = new Date(date);
		expDate.setHours(0, 0, 0, 0);
		const today = new Date();
		today.setHours(0, 0, 0, 0);
		const diffDays = Math.ceil((expDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
		return diffDays <= 3 && diffDays >= 0;
	}

	function isExpired(date: string | null): boolean {
		if (!date) return false;
		const expDate = new Date(date);
		expDate.setHours(0, 0, 0, 0);
		const today = new Date();
		today.setHours(0, 0, 0, 0);
		return expDate < today;
	}

	const groupedItems = $derived(
		pantryItems.reduce(
			(acc, item) => {
				const category = item.ingredient_category;
				if (!acc[category]) acc[category] = [];
				acc[category].push(item);
				return acc;
			},
			{} as Record<IngredientCategory, PantryItem[]>
		)
	);
</script>

<div class="page">
	<div class="page-header">
		<h1>Pantry</h1>
		<div class="header-actions">
			<a href="/suggestions" class="btn btn-success tap-target">What can I cook?</a>
			<button onclick={() => { resetForm(); showForm = true; }} class="btn btn-primary tap-target">Add Item</button>
		</div>
	</div>

	{#if showForm}
		<Card>
			<CardHeader>
				<CardTitle>{editingId ? 'Edit Pantry Item' : 'Add to Pantry'}</CardTitle>
			</CardHeader>
			<CardContent>
				<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="form">
					<div class="form-grid">
						<div class="form-group">
							<label for="ingredient">Ingredient *</label>
							<select
								id="ingredient"
								bind:value={selectedIngredientId}
								required
								disabled={editingId !== null}
								class="input"
							>
								<option value={null}>Select ingredient...</option>
								{#each ingredients as ing}
									<option value={ing.id}>{ing.name}</option>
								{/each}
							</select>
						</div>
						<div class="form-group">
							<label for="quantity">Quantity *</label>
							<input id="quantity" type="number" step="0.01" bind:value={quantity} required class="input" />
						</div>
						<div class="form-group">
							<label for="unit">Unit</label>
							<input id="unit" type="text" bind:value={unit} placeholder="g, ml, pcs..." class="input" />
						</div>
						<div class="form-group">
							<label for="expiration">Expiration Date</label>
							<input id="expiration" type="date" bind:value={expirationDate} class="input" />
						</div>
					</div>
					<div class="form-group">
						<label for="notes">Notes</label>
						<input id="notes" type="text" bind:value={notes} placeholder="Location, brand, etc." class="input" />
					</div>
					<div class="form-actions">
						<button type="submit" class="btn btn-primary tap-target">{editingId ? 'Update' : 'Add'}</button>
						<button type="button" onclick={resetForm} class="btn btn-secondary tap-target">Cancel</button>
					</div>
				</form>
			</CardContent>
		</Card>
	{/if}

	<Card>
		<CardContent>
			<input
				type="text"
				placeholder="Search pantry..."
				bind:value={search}
				oninput={loadPantryItems}
				class="input search-input"
			/>
		</CardContent>
	</Card>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if pantryItems.length === 0}
		<div class="empty-state">Your pantry is empty. Add items to track what you have!</div>
	{:else}
		{#each Object.entries(groupedItems) as [category, items]}
			<Card>
				<CardHeader>
					<CardTitle class="capitalize">{category}</CardTitle>
				</CardHeader>
				<CardContent>
					<div class="item-list">
						{#each items as item}
							<div
								class="item"
								class:expired={isExpired(item.expiration_date)}
								class:expiring={isExpiringSoon(item.expiration_date) && !isExpired(item.expiration_date)}
							>
								<div class="item-info">
									<span class="item-name">{item.ingredient_name}</span>
									<span class="item-qty">{item.quantity} {item.unit || ''}</span>
								</div>
								{#if item.expiration_date}
									<span
										class="exp-badge"
										class:expired={isExpired(item.expiration_date)}
										class:expiring={isExpiringSoon(item.expiration_date) && !isExpired(item.expiration_date)}
									>
										{isExpired(item.expiration_date) ? 'Expired' : ''} {item.expiration_date}
									</span>
								{/if}
								{#if item.notes}
									<span class="notes">{item.notes}</span>
								{/if}
								<div class="item-actions">
									<button onclick={() => startEdit(item)} class="link-btn tap-target">Edit</button>
									<button onclick={() => deleteItem(item.id)} class="link-btn danger tap-target">Remove</button>
								</div>
							</div>
						{/each}
					</div>
				</CardContent>
			</Card>
		{/each}
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
		gap: var(--size-4);
		flex-wrap: wrap;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.header-actions {
		display: flex;
		gap: var(--size-2);
		flex-wrap: wrap;
	}

	.btn {
		padding: var(--size-2) var(--size-4);
		border-radius: var(--radius-2);
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
		cursor: pointer;
		text-decoration: none;
		transition: all 0.2s;
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

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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

	.input:disabled {
		background: var(--color-accent);
	}

	.search-input {
		width: 100%;
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


	.item-list {
		display: flex;
		flex-direction: column;
	}

	.item {
		display: flex;
		align-items: center;
		gap: var(--size-4);
		padding: var(--size-3) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.item:last-child {
		border-bottom: none;
	}

	.item.expired {
		background: rgba(191, 97, 106, 0.1);
	}

	.item.expiring {
		background: rgba(235, 203, 139, 0.1);
	}

	.item-info {
		flex: 1;
		display: flex;
		align-items: center;
		gap: var(--size-2);
	}

	.item-name {
		font-weight: var(--font-weight-6);
	}

	.item-qty {
		color: var(--color-text-muted);
	}

	.exp-badge {
		font-size: var(--font-size-0);
		padding: var(--size-1) var(--size-2);
		border-radius: 9999px;
		background: var(--color-accent);
		color: var(--color-text-muted);
	}

	.exp-badge.expired {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
	}

	.exp-badge.expiring {
		background: rgba(235, 203, 139, 0.2);
		color: #d08770;
	}

	.notes {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.item-actions {
		display: flex;
		gap: var(--size-2);
	}

	.link-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-primary);
		font-size: var(--font-size-1);
	}

	.link-btn:hover {
		text-decoration: underline;
	}

	.link-btn.danger {
		color: var(--color-error);
	}
</style>
