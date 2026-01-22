<script lang="ts">
	import { Card, CardContent, Modal } from '@mskalski/home-ui';
	import type { ShoppingList } from '$lib/types';
	import { api, formatDate, toISODate, getWeekStart, addDays } from '$lib/utils';
	import { onMount } from 'svelte';

	let lists: ShoppingList[] = $state([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreateModal = $state(false);
	let showGenerateModal = $state(false);
	let newListName = $state('');
	let generatingName = $state('');
	let startDate = $state(toISODate(getWeekStart(new Date())));
	let endDate = $state(toISODate(addDays(getWeekStart(new Date()), 6)));

	async function loadLists() {
		loading = true;
		error = null;
		try {
			lists = await api.get<ShoppingList[]>('/shopping-lists');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load shopping lists';
		} finally {
			loading = false;
		}
	}

	onMount(loadLists);

	async function createList() {
		if (!newListName.trim()) return;
		try {
			await api.post('/shopping-lists', { name: newListName });
			newListName = '';
			showCreateModal = false;
			await loadLists();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create list';
		}
	}

	async function generateList() {
		if (!generatingName.trim()) return;
		try {
			await api.post('/shopping-lists/generate', {
				name: generatingName,
				start_date: startDate,
				end_date: endDate
			});
			generatingName = '';
			showGenerateModal = false;
			await loadLists();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to generate list';
		}
	}

	async function deleteList(id: number) {
		if (!confirm('Delete this shopping list?')) return;
		try {
			await api.delete(`/shopping-lists/${id}`);
			await loadLists();
		} catch {
			/* ignore */
		}
	}

	function getProgress(list: ShoppingList): number {
		if (list.items.length === 0) return 0;
		return Math.round((list.items.filter((i) => i.is_checked).length / list.items.length) * 100);
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Shopping Lists</h1>
		<div class="header-actions">
			<button onclick={() => (showGenerateModal = true)} class="btn btn-success">
				Generate from Meals
			</button>
			<button onclick={() => (showCreateModal = true)} class="btn btn-primary">New List</button>
		</div>
	</div>

	{#if error}
		<div class="error-message">{error}</div>
	{/if}

	{#if loading}
		<div class="loading">Loading...</div>
	{:else if lists.length === 0}
		<div class="empty-state">
			No shopping lists yet. Create one or generate from your meal plan!
		</div>
	{:else}
		<div class="list-grid">
			{#each lists as list}
				<Card>
					<CardContent>
						<div class="list-header">
							<div>
								<a href="/shopping-lists/{list.id}" class="list-name">{list.name}</a>
								{#if list.start_date && list.end_date}
									<p class="list-dates">
										{formatDate(list.start_date)} - {formatDate(list.end_date)}
									</p>
								{/if}
							</div>
							<div class="list-actions">
								<a href="/shopping-lists/{list.id}" class="btn btn-sm btn-primary">View</a>
								<button onclick={() => deleteList(list.id)} class="btn btn-sm btn-danger">Delete</button>
							</div>
						</div>
						<div class="progress-section">
							<div class="progress-text">
								{list.items.filter((i) => i.is_checked).length} / {list.items.length} items
							</div>
							<div class="progress-bar">
								<div class="progress-fill" style="width: {getProgress(list)}%"></div>
							</div>
						</div>
					</CardContent>
				</Card>
			{/each}
		</div>
	{/if}
</div>

<Modal
	open={showCreateModal}
	title="New Shopping List"
	onCancel={() => (showCreateModal = false)}
	onConfirm={createList}
	confirmText="Create"
	confirmDisabled={!newListName.trim()}
>
	<div class="modal-form">
		<div class="form-group">
			<label for="listName">Name</label>
			<input id="listName" type="text" bind:value={newListName} required class="input" />
		</div>
	</div>
</Modal>

<Modal
	open={showGenerateModal}
	title="Generate from Meal Plan"
	onCancel={() => (showGenerateModal = false)}
	onConfirm={generateList}
	confirmText="Generate"
	confirmVariant="primary"
	confirmDisabled={!generatingName.trim()}
>
	<div class="modal-form">
		<div class="form-group">
			<label for="genName">Name</label>
			<input
				id="genName"
				type="text"
				bind:value={generatingName}
				placeholder="Weekly Shopping"
				required
				class="input"
			/>
		</div>
		<div class="form-row">
			<div class="form-group">
				<label for="startDate">Start Date</label>
				<input id="startDate" type="date" bind:value={startDate} required class="input" />
			</div>
			<div class="form-group">
				<label for="endDate">End Date</label>
				<input id="endDate" type="date" bind:value={endDate} required class="input" />
			</div>
		</div>
	</div>
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

	.header-actions {
		display: flex;
		gap: var(--size-2);
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

	.btn-sm {
		padding: var(--size-1) var(--size-3);
		font-size: var(--font-size-0);
	}

	.btn-primary {
		background: var(--color-primary);
		color: var(--nord6);
	}

	.btn-primary:hover {
		background: var(--nord9);
	}

	.btn-success {
		background: var(--color-success);
		color: var(--nord6);
	}

	.btn-success:hover {
		opacity: 0.9;
	}

	.btn-danger {
		background: rgba(191, 97, 106, 0.2);
		color: var(--color-error);
	}

	.btn-danger:hover {
		background: rgba(191, 97, 106, 0.3);
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

	.list-grid {
		display: flex;
		flex-direction: column;
		gap: var(--size-4);
	}

	.list-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--size-4);
	}

	.list-name {
		font-size: var(--font-size-3);
		font-weight: var(--font-weight-6);
		color: var(--color-text);
		text-decoration: none;
	}

	.list-name:hover {
		color: var(--color-primary);
	}

	.list-dates {
		font-size: var(--font-size-0);
		color: var(--color-text-muted);
		margin: var(--size-1) 0 0 0;
	}

	.list-actions {
		display: flex;
		gap: var(--size-2);
	}

	.progress-section {
		display: flex;
		align-items: center;
		gap: var(--size-4);
	}

	.progress-text {
		font-size: var(--font-size-1);
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.progress-bar {
		flex: 1;
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
