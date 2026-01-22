<script lang="ts">
	import { Card, CardHeader, CardTitle, CardContent, Modal } from '@mskalski/home-ui';
	import type { ShoppingList, ShoppingListItem, IngredientCategory, Ingredient } from '$lib/types';
	import { api, formatDate } from '$lib/utils';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	let list: ShoppingList | null = $state(null);
	let ingredients: Ingredient[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showAddModal = $state(false);
	let newItemName = $state('');
	let newItemQuantity = $state('');
	let newItemUnit = $state('');
	let selectedIngredientId = $state<number | null>(null);

	const categoryOrder: IngredientCategory[] = [
		'produce', 'dairy', 'meat', 'seafood', 'bakery', 'frozen', 'pantry', 'beverages', 'condiments', 'spices', 'other'
	];

	const categoryLabels: Record<IngredientCategory, string> = {
		produce: 'Produce', dairy: 'Dairy', meat: 'Meat', seafood: 'Seafood', pantry: 'Pantry',
		frozen: 'Frozen', bakery: 'Bakery', beverages: 'Beverages', condiments: 'Condiments', spices: 'Spices', other: 'Other'
	};

	function groupByCategory(items: ShoppingListItem[]): Record<string, ShoppingListItem[]> {
		const groups: Record<string, ShoppingListItem[]> = {};
		for (const item of items) {
			const cat = item.category || 'other';
			if (!groups[cat]) groups[cat] = [];
			groups[cat].push(item);
		}
		return groups;
	}

	async function loadList() {
		loading = true;
		error = null;
		try {
			list = await api.get<ShoppingList>(`/shopping-lists/${$page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load shopping list';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		try {
			ingredients = await api.get<Ingredient[]>('/ingredients');
		} catch {
			/* ignore */
		}
		await loadList();
	});

	async function toggleItem(item: ShoppingListItem) {
		if (!list) return;
		try {
			const updated = await api.post<ShoppingListItem>(`/shopping-lists/${list.id}/items/${item.id}/toggle`);
			item.is_checked = updated.is_checked;
		} catch {
			/* ignore */
		}
	}

	async function deleteItem(item: ShoppingListItem) {
		if (!list) return;
		try {
			await api.delete(`/shopping-lists/${list.id}/items/${item.id}`);
			list.items = list.items.filter((i) => i.id !== item.id);
		} catch {
			/* ignore */
		}
	}

	async function addItem() {
		if (!list || (!newItemName.trim() && !selectedIngredientId)) return;
		try {
			const newItem = await api.post<ShoppingListItem>(`/shopping-lists/${list.id}/items`, {
				ingredient_id: selectedIngredientId,
				name: newItemName.trim() || null,
				quantity: newItemQuantity.trim() || null,
				unit: newItemUnit.trim() || null
			});
			list.items = [...list.items, newItem];
			newItemName = '';
			newItemQuantity = '';
			newItemUnit = '';
			selectedIngredientId = null;
			showAddModal = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to add item';
		}
	}

	function getProgress(): number {
		if (!list || list.items.length === 0) return 0;
		return Math.round((list.items.filter((i) => i.is_checked).length / list.items.length) * 100);
	}
</script>

{#if loading}
	<div class="loading">Loading...</div>
{:else if error}
	<div class="error-message">{error}</div>
{:else if list}
	<div class="page">
		<div class="page-header">
			<div>
				<a href="/shopping-lists" class="back-link">← Back to lists</a>
				<h1>{list.name}</h1>
				{#if list.start_date && list.end_date}
					<p class="dates">{formatDate(list.start_date)} - {formatDate(list.end_date)}</p>
				{/if}
			</div>
			<button onclick={() => (showAddModal = true)} class="btn btn-primary">Add Item</button>
		</div>

		<Card>
			<CardContent>
				<div class="progress-section">
					<span class="progress-text">
						{list.items.filter((i) => i.is_checked).length} / {list.items.length} items checked
					</span>
					<span class="progress-percent">{getProgress()}%</span>
				</div>
				<div class="progress-bar">
					<div class="progress-fill" style="width: {getProgress()}%"></div>
				</div>
			</CardContent>
		</Card>

		{#if list.items.length === 0}
			<div class="empty-state">No items in this list. Add some items to get started!</div>
		{:else}
			{@const grouped = groupByCategory(list.items)}
			{#each categoryOrder as category}
				{#if grouped[category]?.length}
					<Card>
						<CardHeader>
							<CardTitle>{categoryLabels[category]}</CardTitle>
						</CardHeader>
						<CardContent>
							<div class="item-list">
								{#each grouped[category] as item}
									<div class="item" class:checked={item.is_checked}>
										<button onclick={() => toggleItem(item)} class="check-btn" class:done={item.is_checked}>
											{#if item.is_checked}✓{/if}
										</button>
										<div class="item-info" class:done={item.is_checked}>
											<span class="item-name">{item.name}</span>
											{#if item.quantity || item.unit}
												<span class="item-qty">{item.quantity || ''} {item.unit || ''}</span>
											{/if}
											{#if item.added_manually}
												<span class="manual-tag">(manual)</span>
											{/if}
										</div>
										<button onclick={() => deleteItem(item)} class="delete-btn">×</button>
									</div>
								{/each}
							</div>
						</CardContent>
					</Card>
				{/if}
			{/each}
		{/if}
	</div>
{/if}

<Modal
	open={showAddModal}
	title="Add Item"
	onCancel={() => (showAddModal = false)}
	onConfirm={addItem}
	confirmText="Add"
>
	<div class="modal-form">
		{#if ingredients.length > 0}
			<div class="form-group">
				<label for="ingredient">Select Ingredient</label>
				<select id="ingredient" bind:value={selectedIngredientId} class="input">
					<option value={null}>-- Custom item --</option>
					{#each ingredients as ing}
						<option value={ing.id}>{ing.name}</option>
					{/each}
				</select>
			</div>
		{/if}

		{#if !selectedIngredientId}
			<div class="form-group">
				<label for="itemName">Item Name</label>
				<input id="itemName" type="text" bind:value={newItemName} class="input" />
			</div>
		{/if}

		<div class="form-row">
			<div class="form-group">
				<label for="itemQty">Quantity</label>
				<input id="itemQty" type="text" bind:value={newItemQuantity} class="input" />
			</div>
			<div class="form-group">
				<label for="itemUnit">Unit</label>
				<input id="itemUnit" type="text" bind:value={newItemUnit} class="input" />
			</div>
		</div>
	</div>
</Modal>

<style>
	.page {
		max-width: 700px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		gap: var(--size-6);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.back-link {
		font-size: var(--font-size-1);
		color: var(--color-primary);
		text-decoration: none;
	}

	.back-link:hover {
		text-decoration: underline;
	}

	.page-header h1 {
		font-size: var(--font-size-6);
		font-weight: var(--font-weight-8);
		margin: 0;
	}

	.dates {
		color: var(--color-text-muted);
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

	.progress-section {
		display: flex;
		justify-content: space-between;
		margin-bottom: var(--size-2);
	}

	.progress-text {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
	}

	.progress-percent {
		font-size: var(--font-size-1);
		font-weight: var(--font-weight-6);
	}

	.progress-bar {
		height: 8px;
		background: var(--color-accent);
		border-radius: 9999px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: var(--color-success);
		transition: width 0.3s;
	}

	.item-list {
		display: flex;
		flex-direction: column;
	}

	.item {
		display: flex;
		align-items: center;
		gap: var(--size-3);
		padding: var(--size-3) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.item:last-child {
		border-bottom: none;
	}

	.item.checked {
		background: var(--color-bg-muted);
	}

	.check-btn {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		border: 2px solid var(--color-border);
		background: transparent;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: var(--font-size-0);
		transition: all 0.2s;
	}

	.check-btn:hover {
		border-color: var(--color-text-muted);
	}

	.check-btn.done {
		background: var(--color-success);
		border-color: var(--color-success);
		color: var(--nord6);
	}

	.item-info {
		flex: 1;
		display: flex;
		align-items: center;
		gap: var(--size-2);
	}

	.item-info.done {
		color: var(--color-text-muted);
		text-decoration: line-through;
	}

	.item-name {
		font-weight: var(--font-weight-6);
	}

	.item-qty {
		color: var(--color-text-muted);
	}

	.manual-tag {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
	}

	.delete-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--color-error);
		opacity: 0;
		transition: opacity 0.2s;
		padding: var(--size-1) var(--size-2);
	}

	.item:hover .delete-btn {
		opacity: 1;
	}

	.modal-form {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
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
</style>
