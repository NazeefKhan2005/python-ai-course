# Course datasets

The files in this folder are the data for the lessons, exercises and projects of *Python for AI: Zero to Job-Ready*. All of them are fictional and were made for this course, except `glove-mini.json`, a small part of a public-domain set of word vectors.

Download a file from the lesson that uses it, or the whole folder from the course repository, and keep it in a folder called `data/` next to your code.

## Conventions

* Text files use UTF-8 and end each line with `\n`. CSV files have one header row and use commas; a field is quoted only when it contains a comma, a quote or a line break.
* Dates are ISO 8601 (`2026-03-01`). Times use the 24-hour clock (`2026-03-01 13:05:42`) and are local times without a time zone.
* Money is in a generic currency, with two decimals. Distances are in kilometres and areas in square metres.
* A missing value is an empty field in a CSV file and `NULL` in a SQLite database.
* Columns of `yes` and `no` are yes/no answers; columns of `0` and `1` are flags.
* People, companies, restaurants and products are invented. Any resemblance to real ones is a coincidence.

## The files

| File | What it holds | Size | Used in |
|---|---|---|---|
| `server_logs.txt` | One day of logs from an online shop's API server | 1,696 lines | M05-L04, M05 project, M06-L01 |
| `server_logs_large.txt` | A week of logs from the same server | 22,411 lines | M08-L02, M08 project, M10-L05 |
| `images.npz` | Six small images as NumPy arrays | cells (128, 128), checkerboard (128, 128), gradient (64, 256), landscape (120, 160, 3), noisy_shapes (120, 160, 3), shapes (120, 160, 3) | M11-L05, M11 project, E2 |
| `customers.csv` | The customers of an online shop | 1,985 rows × 8 columns | M12, M13-L01 |
| `sales.csv` | The shop's delivered 2025 orders, one row per product line | 11,824 rows × 13 columns | M12, M13-L01 |
| `shop.db` | The shop as a SQLite database | customers 1,985, products 48, orders 7,341, order_items 12,913, employees 43 | M15-L01 to L03 |
| `food_delivery.db` | Restaurants and orders of Colibrí, a food-delivery company | restaurants 150, orders 16,682 | M15, P3 |
| `food_delivery_customers.csv` | Colibrí's customers | 4,778 rows × 7 columns | M15, P3 |
| `food_delivery_promotions.json` | Colibrí's promotion codes, as its promotions API returns them | 12 promotions | P3 |
| `food_delivery_messy.csv` | Colibrí orders exported from its old order system | 2,876 rows × 15 columns | M12-L04, M12 project |
| `student_performance.csv` | Students at a university and their final exam results | 1,000 rows × 15 columns | M13-L03, M13-L04, M14 |
| `housing_small.csv` | Home sales in a city | 1,500 rows × 13 columns | M16-L03, M16 project |
| `telco_churn.csv` | Customers of a telecom company and whether they left | 7,000 rows × 18 columns | M17, M19, P4, M24 |
| `telco_churn_current.csv` | A later batch of the same company's customers | 2,000 rows × 18 columns | M25-L06, P6 |
| `transactions_fraud.csv` | Card payments, some of them fraudulent | 15,000 rows × 13 columns | M16-L07, M17-L07, M25-L07 |
| `sms_small.csv` | Text messages labelled ham (wanted) or spam | 2,400 rows × 3 columns | M18-L05 |
| `books.csv` | The catalogue of an online bookstore | 400 rows × 6 columns | M18-L08, E6, capstone |
| `ratings.csv` | Star ratings that the bookstore's users gave to books | 32,164 rows × 4 columns | M18-L08, E6, capstone |
| `glove-mini.json` | 50-dimensional GloVe word vectors for 2,368 English words | 2,368 words | M22-L02 |
| `docs/` | Colibrí's staff handbook: 18 Markdown pages | 18 pages | M23-L05 to L07, P5 |

## Server logs

`server_logs.txt` covers 2026-03-01 and `server_logs_large.txt` covers 2026-03-02 to 2026-03-08. Each record is one line:

```text
2026-03-01 13:12:08 [ERROR] Database connection lost
```

| Part | Meaning |
|---|---|
| Date and time | When the server wrote the line |
| Level | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`, in square brackets |
| Message | Free text after the level |

Like real logs, `server_logs_large.txt` also contains lines that do not follow this format.

## Images

`images.npz` holds six `uint8` arrays (values 0 to 255). Load it with `np.load("data/images.npz")`.

| Array | Shape | What it shows |
|---|---|---|
| `landscape` | (120, 160, 3) | A colour picture: sky, sun, mountains and grass |
| `shapes` | (120, 160, 3) | Four flat-coloured shapes on a light background |
| `noisy_shapes` | (120, 160, 3) | The same shapes with random noise |
| `checkerboard` | (128, 128) | A grayscale checkerboard |
| `gradient` | (64, 256) | A grayscale ramp from black on the left to white on the right |
| `cells` | (128, 128) | Bright round blobs on a dark background, like cells under a microscope |

## The online shop

An online shop that sells to consumers and businesses in four regions. `customers.csv` and `sales.csv` are exports of `shop.db`.

**`customers.csv`** (also the `customers` table of `shop.db`)

| Column | Meaning |
|---|---|
| `customer_id` | Customer number, from 1001 |
| `name` | Full name |
| `city`, `country` | Where the customer lives |
| `region` | `Africa`, `Americas`, `Asia-Pacific` or `Europe` |
| `segment` | `consumer` or `business` |
| `signup_date` | When the account was created (2022 to 2025) |
| `referred_by` | `customer_id` of the customer who recommended the shop; empty if none |

**`sales.csv`**: one row per product line of each delivered order placed in 2025.

| Column | Meaning |
|---|---|
| `order_id` | Order number; an order with three products has three rows |
| `order_date` | Date of the order |
| `customer_id` | The customer who ordered |
| `region`, `country`, `city` | The customer's location |
| `channel` | `app`, `web` or `phone`; empty when it was not recorded |
| `category`, `product` | What was bought |
| `quantity` | Number of units |
| `unit_price` | Price of one unit before the discount |
| `discount` | Discount as a fraction (0.15 means 15% off) |
| `revenue` | `quantity × unit_price × (1 − discount)`, rounded to 2 decimals |

**`shop.db`** tables:

| Table | Columns |
|---|---|
| `customers` | As in `customers.csv` |
| `products` | `product_id`, `name`, `category`, `unit_price`, `unit_cost` |
| `orders` | `order_id`, `customer_id`, `order_date`, `channel`, `status` (`delivered`, `returned` or `cancelled`); orders of every status from 2025 |
| `order_items` | `order_id`, `product_id`, `quantity`, `unit_price`, `discount` |
| `employees` | `employee_id`, `name`, `department`, `job_title`, `manager_id` (the employee's manager; `NULL` for the chief executive), `hire_date`, `salary` (per year) |

## Colibrí, a food-delivery company

Colibrí delivers food from restaurants in Bogotá, Lima, Medellín, Cali and Quito. The data covers 2025-01-01 to 2026-09-30. The staff handbook in `docs/` belongs to the same company. Customers are pseudonymised: there are no names.

**`food_delivery.db`** tables:

| Table | Column | Meaning |
|---|---|---|
| `restaurants` | `restaurant_id`, `name` | Restaurant number and name |
| | `cuisine` | One of 15 cuisines, such as `Colombian`, `Peruvian` or `Pizza` |
| | `city` | The restaurant's city |
| | `price_level` | 1 (cheap) to 3 (expensive) |
| | `joined_on` | When the restaurant joined Colibrí |
| `orders` | `order_id` | Order number |
| | `customer_id`, `restaurant_id` | Who ordered, from where |
| | `ordered_at` | Date and time of the order |
| | `items` | Number of dishes |
| | `subtotal` | Price of the food |
| | `delivery_fee` | Fee paid by the customer |
| | `discount` | Discount from a promotion code |
| | `total` | `subtotal + delivery_fee − discount` |
| | `promo_code` | The promotion code used; `NULL` if none |
| | `payment_method` | `card`, `cash` or `wallet` |
| | `distance_km` | Distance from the restaurant to the customer |
| | `promised_minutes` | Delivery time promised at checkout |
| | `delivery_minutes` | Actual delivery time; `NULL` for cancelled orders |
| | `status` | `delivered` or `cancelled` |
| | `rating` | The customer's rating, 1 to 5; `NULL` if the customer did not rate |

**`food_delivery_customers.csv`**

| Column | Meaning |
|---|---|
| `customer_id` | Customer number, from 50001 |
| `city` | The customer's city |
| `signup_date` | When the customer created an account |
| `acquisition_channel` | How the customer found Colibrí: `organic`, `referral`, `paid_social`, `search` or `partner_promo` |
| `platform` | `android`, `ios` or `web` |
| `age_band` | `18-24`, `25-34`, `35-44`, `45-54` or `55+` |
| `marketing_opt_in` | `yes` if the customer agreed to receive marketing messages |

**`food_delivery_promotions.json`** is an object with one key, `promotions`: a list of objects with these keys.

| Key | Meaning |
|---|---|
| `promo_code` | The code customers enter, such as `WELCOME20` |
| `name` | A description of the offer |
| `kind` | `percent_off`, `amount_off` or `free_delivery` |
| `value` | The percentage or the amount; `null` for free delivery |
| `audience` | Who can use it, such as `new customers` |
| `cities` | The cities where it works |
| `start_date`, `end_date` | When it works; an `end_date` of `null` means it has no end |

**`food_delivery_messy.csv`** is an export of the orders from January to March 2026, made by Colibrí's old order system. Its columns are `order_id`, `order_time`, `customer_id`, `restaurant` (the name), `cuisine`, `city`, `items`, `subtotal`, `delivery_fee`, `total`, `payment`, `status`, `distance_km`, `delivery_minutes` and `rating`, with the same meanings as in the database. The export has the problems that real exports have: finding and fixing them is the M12 project.

## Students

**`student_performance.csv`**: one row per student.

| Column | Meaning |
|---|---|
| `student_id` | `S0001` to `S1000` |
| `programme` | The student's degree programme |
| `year` | Year of study, 1 to 3 |
| `age` | Age in years |
| `previous_grade` | Average grade of the previous year, 0 to 100 |
| `study_hours` | Hours of study per week, as the student reported |
| `attendance_pct` | Percentage of classes attended |
| `sleep_hours` | Average hours of sleep per night |
| `work_hours` | Hours of paid work per week |
| `commute_minutes` | Travel time to the university, one way |
| `tutoring` | `yes` if the student took part in the tutoring programme |
| `internet_at_home` | `yes` or `no` |
| `extracurricular` | `yes` if the student takes part in clubs or sports |
| `final_exam` | Final exam score, 0 to 100 |
| `passed` | `yes` if `final_exam` is at least 50 |

## Housing

**`housing_small.csv`**: one row per home sold. The target is `price`.

| Column | Meaning |
|---|---|
| `district` | One of 8 districts of the city |
| `property_type` | `apartment`, `terraced house` or `detached house` |
| `area_m2` | Living area |
| `bedrooms`, `bathrooms` | Number of rooms |
| `year_built` | Year of construction |
| `distance_centre_km` | Distance to the city centre |
| `distance_station_km` | Distance to the nearest train station |
| `garden`, `parking` | `yes` or `no` |
| `energy_rating` | `A` (best) to `G` (worst) |
| `condition` | 1 (poor) to 5 (excellent) |
| `price` | Sale price |

## Telecom churn

**`telco_churn.csv`** describes the customers of a telecom company on 2026-06-30; `churn` says who left in July 2026. **`telco_churn_current.csv`** has the same columns for customers three months later.

| Column | Meaning |
|---|---|
| `customer_id` | `C-100001` onwards (`C-200001` onwards in the later batch) |
| `region` | `North`, `South`, `East`, `West` or `Central` |
| `age_band` | `18-24` to `65+` |
| `tenure_months` | Months as a customer |
| `contract` | `month-to-month`, `one-year` or `two-year` |
| `payment_method` | How the customer pays |
| `paperless_billing` | `yes` or `no` |
| `internet_service` | `fibre`, `dsl` or `none` |
| `streaming_tv`, `tech_support` | Extra services: `yes` or `no` |
| `mobile_lines` | Number of mobile lines |
| `monthly_charges` | The monthly bill |
| `total_charges` | Everything the customer has paid; empty for customers in their first month |
| `data_usage_gb` | Mobile and home data used last month |
| `support_calls_90d` | Calls to support in the last 90 days |
| `late_payments_12m` | Late payments in the last 12 months |
| `satisfaction` | Survey answer, 1 to 5; empty if the customer did not answer |
| `churn` | `yes` if the customer left |

## Card payments

**`transactions_fraud.csv`**: card payments in April 2026, one row per payment, in time order.

| Column | Meaning |
|---|---|
| `transaction_id` | `T0000001` onwards |
| `timestamp` | Date and time of the payment |
| `card_id` | The card used; several rows can share a card |
| `amount` | Amount paid |
| `merchant_category` | Such as `grocery`, `fuel`, `electronics` or `gift_cards` |
| `channel` | `in_store`, `contactless` or `online` |
| `is_foreign` | 1 if the merchant is in another country |
| `distance_from_home_km` | Distance from the cardholder's home to where the payment was made (the shop, or the device for online payments) |
| `card_age_days` | Days since the card was issued |
| `txn_last_24h` | Payments with the same card in the 24 hours before this one |
| `avg_amount_30d` | The card's average payment over the previous 30 days |
| `new_device` | 1 if an online payment came from a device not seen before |
| `is_fraud` | 1 if the payment was fraudulent |

## Text messages

**`sms_small.csv`** has the columns `id`, `label` (`ham` or `spam`) and `text`. The messages were written for this course from templates; they are not the UCI SMS Spam Collection. Links use the reserved `.example` domain, so none of them work.

## Books and ratings

**`books.csv`**

| Column | Meaning |
|---|---|
| `book_id` | 1 to 400 |
| `title`, `author` | Invented titles and authors |
| `genre` | One of 12 genres, such as `fantasy` or `cooking` |
| `year` | Year of publication |
| `pages` | Number of pages |

**`ratings.csv`**: each user rated each book at most once.

| Column | Meaning |
|---|---|
| `user_id` | 1 to 900 |
| `book_id` | The book rated |
| `rating` | 1 to 5 stars |
| `rated_at` | When the rating was given (2024 to 2026) |

## Word vectors

**`glove-mini.json`** is one JSON object: each key is a lowercase English word and each value a list of 50 numbers (rounded to 4 decimals). It contains the 2,000 most frequent purely alphabetic words of GloVe's vocabulary plus 368 words chosen for the lessons: word pairs for analogies (countries and capitals, verb forms, comparatives, plurals), categories of things, and job titles for measuring bias. The words are in GloVe's frequency order.

## The Colibrí handbook

**`docs/`** holds 18 Markdown pages from Colibrí's staff handbook: working hours, leave, expenses, security, privacy, on-call, data definitions, customer support and more. Each page starts with a header between `---` lines:

| Field | Meaning |
|---|---|
| `id` | Page identifier, such as `hr-003` |
| `title` | Page title |
| `owner` | The team responsible for the page |
| `updated` | Date of the last change |
| `status` | `current`, or `archived` for an old version kept for reference |
| `replaced_by` | For an archived page, the `id` of the page that replaced it |
| `audience` | Who the page is for |

`docs/bogota-office-notes.md` is a wiki page that anyone can edit, and it contains an instruction aimed at AI assistants on purpose: M23-L07 uses it to show indirect prompt injection.

## Licences and sources

* **Everything except `glove-mini.json`** was created for this course and is dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/): you may copy, change and share it for any purpose without asking.
* **`glove-mini.json`** is a subset of the GloVe vectors `glove.6B.50d.txt` from [stanfordnlp/GloVe](https://github.com/stanfordnlp/GloVe), made available under the [Open Data Commons Public Domain Dedication and License (PDDL) 1.0](https://opendatacommons.org/licenses/pddl/1-0/). Please cite: Jeffrey Pennington, Richard Socher and Christopher D. Manning. 2014. *GloVe: Global Vectors for Word Representation*. In Proceedings of EMNLP 2014, pages 1532–1543. The subset was cut from the file `glove.6B.50d.txt` (SHA-256 `c99ba128d1efdaa3496b7542ba599ecdd1dd6679114d3b5ce19f0ec208b4aa5b`) inside `glove.6B.zip` from the project's official download.

## Not in this folder

* **Pretrained models and bigger datasets** are downloaded by the notebooks that use them, once, on your own computer; the course does not redistribute them.
* **scikit-learn's bundled datasets** (`load_iris`, `load_wine`, `load_digits` and others) come with scikit-learn.

## Rebuilding the files

The generated files come from `tools/make_datasets.py` in the course repository. Every dataset has a fixed random seed, so the files are identical on every run:

```bash
python tools/make_datasets.py            # rebuild every generated file
python tools/make_datasets.py --list     # files, sizes and shapes
python tools/make_datasets.py --check    # compare this folder with a fresh run
```

`glove-mini.json` is rebuilt only from the original download, with `python tools/make_datasets.py --glove glove.6B.zip`. The handbook in `docs/` was written by hand.
