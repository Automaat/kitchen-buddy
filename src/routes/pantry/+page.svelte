<script lang="ts">
	import type { PantryItem, Ingredient, IngredientCategory } from '$lib/types';
	import { api, getImageUrl } from '$lib/utils';
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

	const categoryColors: Record<IngredientCategory, string> = {
		produce: 'bg-green-100 text-green-800',
		dairy: 'bg-blue-100 text-blue-800',
		meat: 'bg-red-100 text-red-800',
		seafood: 'bg-cyan-100 text-cyan-800',
		pantry: 'bg-amber-100 text-amber-800',
		frozen: 'bg-indigo-100 text-indigo-800',
		bakery: 'bg-orange-100 text-orange-800',
		beverages: 'bg-purple-100 text-purple-800',
		condiments: 'bg-yellow-100 text-yellow-800',
		spices: 'bg-rose-100 text-rose-800',
		other: 'bg-gray-100 text-gray-800'
	};

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

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h1 class="text-3xl font-bold text-gray-900">Pantry</h1>
		<div class="flex gap-2">
			<a
				href="/suggestions"
				class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
			>
				What can I cook?
			</a>
			<button
				onclick={() => {
					resetForm();
					showForm = true;
				}}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				Add Item
			</button>
		</div>
	</div>

	{#if showForm}
		<div class="bg-white p-6 rounded-lg shadow-sm border">
			<h2 class="text-lg font-semibold mb-4">
				{editingId ? 'Edit Pantry Item' : 'Add to Pantry'}
			</h2>
			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleSubmit();
				}}
				class="space-y-4"
			>
				<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
					<div>
						<label for="ingredient" class="block text-sm font-medium text-gray-700 mb-1">
							Ingredient *
						</label>
						<select
							id="ingredient"
							bind:value={selectedIngredientId}
							required
							disabled={editingId !== null}
							class="w-full px-4 py-2 border rounded-lg disabled:bg-gray-100"
						>
							<option value={null}>Select ingredient...</option>
							{#each ingredients as ing}
								<option value={ing.id}>{ing.name}</option>
							{/each}
						</select>
					</div>
					<div>
						<label for="quantity" class="block text-sm font-medium text-gray-700 mb-1">
							Quantity *
						</label>
						<input
							id="quantity"
							type="number"
							step="0.01"
							bind:value={quantity}
							required
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="unit" class="block text-sm font-medium text-gray-700 mb-1">Unit</label>
						<input
							id="unit"
							type="text"
							bind:value={unit}
							placeholder="g, ml, pcs..."
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
					<div>
						<label for="expiration" class="block text-sm font-medium text-gray-700 mb-1">
							Expiration Date
						</label>
						<input
							id="expiration"
							type="date"
							bind:value={expirationDate}
							class="w-full px-4 py-2 border rounded-lg"
						/>
					</div>
				</div>
				<div>
					<label for="notes" class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
					<input
						id="notes"
						type="text"
						bind:value={notes}
						placeholder="Location, brand, etc."
						class="w-full px-4 py-2 border rounded-lg"
					/>
				</div>
				<div class="flex gap-2">
					<button
						type="submit"
						class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
					>
						{editingId ? 'Update' : 'Add'}
					</button>
					<button
						type="button"
						onclick={resetForm}
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	{/if}

	<div class="bg-white p-4 rounded-lg shadow-sm border">
		<input
			type="text"
			placeholder="Search pantry..."
			bind:value={search}
			oninput={loadPantryItems}
			class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
		/>
	</div>

	{#if error}
		<div class="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
	{/if}

	{#if loading}
		<div class="text-center py-12">Loading...</div>
	{:else if pantryItems.length === 0}
		<div class="text-center py-12 text-gray-500">
			Your pantry is empty. Add items to track what you have!
		</div>
	{:else}
		{#each Object.entries(groupedItems) as [category, items]}
			<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
				<div class="bg-gray-50 px-4 py-2 border-b">
					<h2 class="font-semibold capitalize">{category}</h2>
				</div>
				<div class="divide-y">
					{#each items as item}
						<div
							class="px-4 py-3 flex items-center justify-between hover:bg-gray-50"
							class:bg-red-50={isExpired(item.expiration_date)}
							class:bg-yellow-50={isExpiringSoon(item.expiration_date) &&
								!isExpired(item.expiration_date)}
						>
							<div class="flex items-center gap-4">
								<div>
									<span class="font-medium">{item.ingredient_name}</span>
									<span class="text-gray-500 ml-2">
										{item.quantity}
										{item.unit || ''}
									</span>
								</div>
								{#if item.expiration_date}
									<span
										class="text-xs px-2 py-0.5 rounded-full"
										class:bg-red-100={isExpired(item.expiration_date)}
										class:text-red-700={isExpired(item.expiration_date)}
										class:bg-yellow-100={isExpiringSoon(item.expiration_date) &&
											!isExpired(item.expiration_date)}
										class:text-yellow-700={isExpiringSoon(item.expiration_date) &&
											!isExpired(item.expiration_date)}
										class:bg-gray-100={!isExpired(item.expiration_date) &&
											!isExpiringSoon(item.expiration_date)}
										class:text-gray-600={!isExpired(item.expiration_date) &&
											!isExpiringSoon(item.expiration_date)}
									>
										{isExpired(item.expiration_date) ? 'Expired' : ''} {item.expiration_date}
									</span>
								{/if}
								{#if item.notes}
									<span class="text-sm text-gray-500">{item.notes}</span>
								{/if}
							</div>
							<div class="flex gap-2">
								<button onclick={() => startEdit(item)} class="text-blue-600 hover:underline">
									Edit
								</button>
								<button onclick={() => deleteItem(item.id)} class="text-red-600 hover:underline">
									Remove
								</button>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/each}
	{/if}
</div>
