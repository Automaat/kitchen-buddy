<script lang="ts">
	import '@mskalski/home-ui/styles';
	import { Navbar } from '@mskalski/home-ui';
	import { page } from '$app/stores';

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: '🏠' },
		{ href: '/recipes', label: 'Recipes', icon: '📖' },
		{ href: '/collections', label: 'Collections', icon: '📚' },
		{ href: '/meal-planner', label: 'Meal Planner', icon: '📅' },
		{ href: '/shopping-lists', label: 'Shopping Lists', icon: '🛒' },
		{ href: '/pantry', label: 'Pantry', icon: '🗄️' },
		{ href: '/suggestions', label: 'Suggestions', icon: '💡' },
		{ href: '/ingredients', label: 'Ingredients', icon: '🥕' },
		{ href: '/favorites', label: 'Favorites', icon: '⭐' }
	];

	let { children } = $props();
</script>

<div class="app">
	<Navbar items={navItems} brand="🍳 Kitchen Buddy" currentPath={$page.url.pathname} />

	<main class="main">
		{@render children()}
	</main>
</div>

<style>
	.app {
		display: flex;
		min-height: 100vh;
	}

	.main {
		flex: 1;
		padding: var(--size-4);
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
	}

	@media (max-width: 767px) {
		.main {
			padding-top: calc(var(--size-3) * 2 + 48px);
		}
	}

	@media (min-width: 768px) {
		.main {
			padding: var(--size-5);
		}
	}

	@media (min-width: 1024px) {
		.main {
			padding: var(--size-6);
		}
	}
</style>
