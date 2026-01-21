export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';
export type DifficultyLevel = 'easy' | 'medium' | 'hard';
export type IngredientCategory =
	| 'produce'
	| 'dairy'
	| 'meat'
	| 'seafood'
	| 'pantry'
	| 'frozen'
	| 'bakery'
	| 'beverages'
	| 'condiments'
	| 'spices'
	| 'other';

export interface Tag {
	id: number;
	name: string;
	created_at: string;
}

export interface Ingredient {
	id: number;
	name: string;
	category: IngredientCategory;
	default_unit: string | null;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface RecipeIngredient {
	id: number;
	ingredient_id: number;
	ingredient_name: string;
	quantity: string | null;
	unit: string | null;
	notes: string | null;
}

export interface RecipeImage {
	id: number;
	is_primary: boolean;
	sort_order: number;
	created_at: string;
}

export interface RecipeListItem {
	id: number;
	title: string;
	description: string | null;
	prep_time_minutes: number | null;
	cook_time_minutes: number | null;
	servings: number;
	difficulty: DifficultyLevel;
	is_favorite: boolean;
	primary_image_id: number | null;
	tags: Tag[];
	created_at: string;
}

export interface Recipe {
	id: number;
	title: string;
	description: string | null;
	instructions: string | null;
	prep_time_minutes: number | null;
	cook_time_minutes: number | null;
	servings: number;
	difficulty: DifficultyLevel;
	is_active: boolean;
	is_favorite: boolean;
	ingredients: RecipeIngredient[];
	images: RecipeImage[];
	tags: Tag[];
	created_at: string;
	updated_at: string;
}

export interface RecipeSummary {
	id: number;
	title: string;
	primary_image_id: number | null;
}

export interface MealPlan {
	id: number;
	date: string;
	meal_type: MealType;
	recipe_id: number;
	servings: number;
	notes: string | null;
	is_completed: boolean;
	recipe: RecipeSummary;
	created_at: string;
	updated_at: string;
}

export interface WeekMealPlan {
	start_date: string;
	end_date: string;
	meals: MealPlan[];
}

export interface ShoppingListItem {
	id: number;
	ingredient_id: number | null;
	name: string | null;
	quantity: string | null;
	unit: string | null;
	is_checked: boolean;
	added_manually: boolean;
	category: IngredientCategory | null;
	created_at: string;
}

export interface ShoppingList {
	id: number;
	name: string;
	start_date: string | null;
	end_date: string | null;
	is_active: boolean;
	items: ShoppingListItem[];
	created_at: string;
	updated_at: string;
}

export interface Dashboard {
	total_recipes: number;
	total_ingredients: number;
	total_favorites: number;
	todays_meals: MealPlan[];
}

export interface ScaledIngredient {
	ingredient_id: number;
	ingredient_name: string;
	original_quantity: string | null;
	scaled_quantity: string | null;
	unit: string | null;
	notes: string | null;
}
