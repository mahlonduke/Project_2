DROP TABLE IF EXISTS sales;

CREATE TABLE IF NOT EXISTS sales (
	sale_id SERIAL PRIMARY KEY,
	lat FLOAT,
	lon FLOAT,
	squarefeet INT,
	yearBuilt INT,
	bathrooms FLOAT,
	bedrooms INT,
	salePrice FLOAT
);

DROP TABLE IF EXISTS summary;

CREATE TABLE IF NOT EXISTS summary (
	summary_id SERIAL PRIMARY KEY,
	city VARCHAR(20),
	totalProperties INT,
	pricePerBed FLOAT,
	pricePerBath FLOAT,
	pricePerSquareFoot FLOAT,
	averageBeds INT,
	averageBaths INT,
	averageYearBuilt INT
);
