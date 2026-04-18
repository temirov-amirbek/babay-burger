-- =============================================
--  BABAY BURGER BOT — Database Schema + Seed
-- =============================================

-- Kategoriyalar
INSERT INTO categories (name_uz, name_ru, name_en, emoji, type, "order") VALUES
('Burgerlar',   'Бургеры',   'Burgers',   '🍔', 'burger',  1),
('Ichimliklar', 'Напитки',   'Drinks',    '🥤', 'drink',   2),
('Setlar',      'Сеты',      'Sets',      '🎁', 'set',     3),
('Dessertlar',  'Десерты',   'Desserts',  '🍰', 'dessert', 4),
('Sneklar',     'Снеки',     'Snacks',    '🍟', 'snack',   5)
ON CONFLICT DO NOTHING;

-- Mahsulotlar (namuna)
INSERT INTO products (category_id, name_uz, name_ru, name_en,
    description_uz, description_ru, description_en, price, is_available, "order") VALUES
-- Burgerlar
(1, 'Babay Classic', 'Бабай Классик', 'Babay Classic',
 '200g mol go''shti, salat, pomidor, pishloq, maxsus sous',
 '200г говядина, салат, томат, сыр, фирменный соус',
 '200g beef, lettuce, tomato, cheese, special sauce', 32000, true, 1),

(1, 'BBQ Burger', 'BBQ Бургер', 'BBQ Burger',
 '250g mol go''shti, BBQ sous, makkajo''xori, pishloq',
 '250г говядина, соус BBQ, кукуруза, сыр',
 '250g beef, BBQ sauce, corn, cheese', 38000, true, 2),

(1, 'Chicken Crispy', 'Хрустящий Чикен', 'Chicken Crispy',
 'Crispy tovuq go''shti, slaw sous, pickles',
 'Хрустящая курица, соус слоу, маринованные огурцы',
 'Crispy chicken, slaw sauce, pickles', 28000, true, 3),

(1, 'Double Smash', 'Двойной Смэш', 'Double Smash',
 '2x150g smash kotlet, ikki qatlam pishloq',
 '2x150г смэш-котлет, двойной сыр',
 '2x150g smash patty, double cheese', 45000, true, 4),

-- Ichimliklar
(2, 'Coca-Cola 0.5L', 'Кока-Кола 0.5L', 'Coca-Cola 0.5L',
 'Muzli Coca-Cola', 'Ледяная Кока-Кола', 'Iced Coca-Cola', 8000, true, 1),

(2, 'Limonad', 'Лимонад', 'Lemonade',
 'Uy limonadi, tabiiy ingredients', 'Домашний лимонад', 'Homemade lemonade', 12000, true, 2),

(2, 'Milkshake', 'Милкшейк', 'Milkshake',
 'Qulupnay / Shokolad / Vanil', 'Клубника / Шоколад / Ваниль', 'Strawberry / Chocolate / Vanilla', 18000, true, 3),

-- Setlar
(3, 'Classic Set', 'Классик Сет', 'Classic Set',
 'Babay Classic + Coca-Cola + Kartoshka fri',
 'Бабай Классик + Кока-Кола + Картофель фри',
 'Babay Classic + Coca-Cola + French fries', 55000, true, 1),

(3, 'Family Set', 'Семейный Сет', 'Family Set',
 '4 Burger + 4 Ichimlik + 2 Kartoshka fri',
 '4 Бургера + 4 Напитка + 2 Картофель фри',
 '4 Burgers + 4 Drinks + 2 French fries', 185000, true, 2),

-- Sneklar
(5, 'Kartoshka Fri', 'Картофель Фри', 'French Fries',
 'Crispy kartoshka fri, sous bilan', 'Хрустящая картошка фри с соусом', 'Crispy fries with dip', 12000, true, 1)
ON CONFLICT DO NOTHING;

-- Promo kodlar (namuna)
INSERT INTO promo_codes (code, discount_percent, discount_amount, max_uses, is_active) VALUES
('BABAY10',  10, 0,     100, true),
('WELCOME',  0,  5000,  50,  true),
('BIGORDER', 15, 0,     20,  true)
ON CONFLICT DO NOTHING;
