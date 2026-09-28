# Bike Sharing Demand — Neural Network Predictor

## About the project

This project uses the **Kaggle Bike Sharing Demand dataset** from Capital Bikeshare in Washington, D.C.

The dataset contains hourly bike rental data from 2011 and 2012. For each hour, we have things like:

* Temperature
* Humidity
* Windspeed
* Weather
* Season
* Holiday / working day
* Number of bikes rented

The main goal is simple:

**Given the weather and time information, can we predict how many bikes will be rented in that hour?**

This could be useful for planning bike availability or knowing when demand is likely to be high.

Kaggle only provides the 1st–19th day of each month for training. The remaining days are used for their leaderboard, so I couldn't use those to check my own model.

---

## What I did

The overall process was pretty straightforward:

1. **Checked the data first**

   * Looked for missing values and duplicates.
   * Checked the categorical columns.
   * Looked at the distribution of the rental count.

2. **Cleaned some data**

   * Some humidity values were `0`, which doesn't make much sense, so I treated them as sensor errors and filled them with an estimate.
   * Windspeed was also `0` quite often, so I flagged that as something to be aware of.

3. **Created useful features**

   * Extracted year, month, day and hour from the timestamp.
   * One-hot encoded `weather` and `season`.
   * Removed a few columns that were basically giving duplicate information.

4. **Scaled the numerical features**

   * Used `StandardScaler`.
   * The scaler was fitted only on the training data.

5. **Built a neural network**

   * Used PyTorch.
   * The model predicts `log1p(count)` instead of the raw rental count.

6. **Tuned the model**

   * Used Optuna to find better values for learning rate, weight decay, batch size and hidden-layer sizes.
   * A separate validation set was used during tuning.

7. **Tested the final model**

   * The test set was kept completely separate until the end.

8. **Made it usable**

   * Added a command-line prediction tool.
   * Also made a small Tkinter desktop GUI.

Basically, notebook ma matra model rakheko chaina — prediction garna directly use garna milne banayeko chu.

---

## Why I made these choices

### Using `log1p(count)`

The rental count is quite skewed. Most hours have a reasonable number of rentals, while some rush-hour periods have much higher numbers.

Training directly on the raw count can make the model focus too much on those big values.

So I trained it using:

```python
log1p(count)
```

After prediction, I converted it back using `expm1`.

---

### Dropping `atemp`

`atemp` is the "feels-like" temperature.

It has a correlation of around **0.98** with the actual temperature, so they are basically telling the model the same thing.

Keeping both didn't add much, so I dropped `atemp`.

---

### Dropping `minute`

Every row in this dataset is recorded exactly on the hour, so `minute` is always `0`.

Since it never changes, there isn't really any reason to give it to the model.

---

### Handling categorical columns

`holiday` and `workingday` are already `0/1` values, so I kept them that way.

For columns with multiple categories, such as `weather` and `season`, I used one-hot encoding.

---

### Scaling

I scaled the continuous features such as:

* Temperature
* Humidity
* Windspeed
* Calendar-related numerical values

The binary and one-hot encoded columns were left as they were.

---

## Train / validation / test split

I used three separate sets instead of only train and test.

The idea is:

**Train → learn the model**

**Validation → tune the model**

**Test → final evaluation**

This is important because using the test set while tuning can make the final score look better than it actually is.

The test set was only used at the very end.

---

## Why Optuna?

Instead of manually guessing the hyperparameters, I used **Optuna**.

It searched for combinations of:

* Learning rate
* Weight decay
* Batch size
* Hidden-layer sizes

Each trial also used early stopping, so poorly performing models didn't keep training unnecessarily.

---

## Model

The neural network is a small feed-forward network built with PyTorch.

Nothing too complicated — just `Linear` and `ReLU` layers.

The idea is to let the network learn relationships between things like weather, time and working days.

For example, rush hour can behave very differently depending on whether it's a working day or a holiday.

Optuna ran **20 trials**.

The best architecture ended up being:

```text
64 → 32 → 16
```

The final model was then trained using those settings and evaluated on the untouched test set.

---

## Saving the model

I saved more than just the model weights.

The checkpoint also contains:

* Scaler information
* Feature names
* Hidden-layer sizes
* Model weights

This is useful because the prediction code needs to recreate the exact same model structure.

Otherwise, model load garda architecture mismatch huna sakcha.

---

## Making predictions

The main prediction logic is inside `predict.py`.

It takes a dictionary of input values and returns the predicted bike rental count.

There are two ways to use it:

* `predict_cli.py` — command line
* `Regression_GUI.py` — desktop GUI

Both use the same prediction function, so the actual prediction logic only needs to be maintained in one place.

---

## Results

The final results on the held-out test set were:

| Model          |   RMSE |    MAE |     R² |
| -------------- | -----: | -----: | -----: |
| Neural Network |  54.98 |  34.46 |  0.909 |
| Mean baseline  | 181.90 | 142.23 | ~0.000 |

The neural network achieved an **R² of 0.909**, meaning it explains around 91% of the variation in hourly bike demand.

The MAE was **34.46**, so the predictions were off by about 34 rentals on average.

For this dataset, that's a pretty useful result.

---

## Best hyperparameters

Optuna found:

```text
Hidden layers: 64, 32, 16
Learning rate: ~0.0016
Batch size: 64
```

Training stopped after **96 epochs** because the validation loss stopped improving.

---

## Limitations

The model still struggles with some extreme cases.

For example, hours with unusually high demand are harder to predict because there aren't many of those examples in the training data.

So basically, normal demand is easier for the model, while unusual rush-hour spikes are more difficult.

This is one of the main limitations of the dataset and not necessarily something that can be fixed just by making the neural network bigger.

---

## Project structure

The main files are:

```text
bike_demand_nn.ipynb    # Training and experimentation
predict.py              # Main prediction logic
predict_cli.py          # Command-line prediction
Regression_GUI.py       # Desktop GUI
```

The notebook handles the data preparation, feature engineering, training and evaluation.

The other files are there so the trained model can actually be used without opening the notebook.
