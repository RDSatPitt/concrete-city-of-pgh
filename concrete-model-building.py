import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium", app_title="ConCReTE Model Building")

@app.cell(hide_code = True)
def _(mo):
    input_key = mo.ui.text(label="Groq AI API key", kind="password")
    input_key
    return input_key

@app.cell(hide_code=True)
def _(mo, input_key):
    context = """
        # **ConCReTE: City of Pittsburgh Module**
        ---
        ## **The Story So Far**
        The City of Pittsburgh is implementing a three-year data strategy under the leadership of Chris Belasco, Senior Manager of Digital Services and Chief Data Officer. This strategy positions data as a critical asset to enhance city operations, engage the community, and drive equity. The city focuses on improving data accessibility and quality while fostering a culture of insight-driven decision-making. Participants in this initiative are tasked with analyzing and forecasting the city’s revenue, which is critical for supporting Pittsburgh’s long-term goals. Prior to the start of this scenario, Chris's team has:

        1. Identified a need to forecast the city's revenue.
        2. Reviewed historical revenue data and identfied the specific tables needed in the City's Revenue Report PDfs; namely, the Q4 Revenue Summary Table from each report and the Quarterly Revenue Totals (Actual, not projected) from each table.
        3. Downloaded the Revenue Report PDFs and extracted the Q4 Revenue Summary Tables into separate documents.
        4. Used six different methodologies to extract the actual quarterly revenue totals from each PDF table.
            - Manual Extraction by a Human
            - Automated Extraction with Docling
            - Automated Extraction with One-Shot AI ChatBot (Claude & ChatGPT)
            - Automated Extraction Claude API (PDF & Images)
            - Automated Extraction with pypdf

        ### Role
        You are an intern working for Chris, and he has asked you to help out with this next stage of the project.

        ### Business Objective
        You want to use the historical quarterly revenue data to create a predictive model for the city's revenue.
        Beyond creating an accurate predictive model, you will need to consider what the most appropriate way to approach parsing the data is.

        ### Data
        We have a dataset of the city's quarterly revenue from 2012 to 2023.

        ---
        """

    rdso_1 = """
    ### *RDSO 1: Evaluate*
    _What previous decisions might have been made that impact your work here? Would your answer change if your role was different?_
    """

    rdso_2 = """
    ### *RDSO 2: Predict*
    _Before selecting from one of the 6 options below, consider each option carefully. Do any of them raise technical or ethical concerns?_
    """

    rdso_3 = """
    ### *RDSO 3: Synthesize*
    _What are your thoughts on using data extracted by AI? Did it affect the quality of your model?_
    """

    system_message = "You are reviewing the work of a student learning responsible data science skills. Attached is the context to the scenario they are working within, as well as the three prompts they will be responding to in order. Your job is to provide them with feedback on each response in the form of a single follow-up question. Once they respond to your follow-up, encourage them to move to the next part of the scenario."

    # build a single plain-string system message
    sys_msg = system_message + "\n\n" + context + "\n\n" + rdso_1 + "\n\n" + rdso_2 + "\n\n" + rdso_3

    reactive_chat = mo.ui.chat(
       mo.ai.llm.groq(
           model="llama-3.1-8b-instant",
           system_message=sys_msg,
           api_key=input_key.value,
       ),
    )

    mo.vstack([mo.md(context), mo.vstack([mo.md(rdso_1), reactive_chat]).callout()])
    return rdso_2, rdso_3, reactive_chat


@app.cell(hide_code=True)
def _(mo, pd):
    # create data path
    data_path = mo.notebook_location() / "data" / "all_extracted_data.csv"

    # load the data
    pgh_revenue_data = pd.read_csv(data_path)
    # create a new column that is the year and quarter combined
    pgh_revenue_data['Year-Quarter'] = pgh_revenue_data['year'].astype(str) + '-' + pgh_revenue_data['quarter']
    return (pgh_revenue_data,)


@app.cell(hide_code=True)
def _(
    is_ai_source,
    mo,
    pgh_revenue_data,
    rdso_2,
    reactive_chat,
    revenue_selector,
):
    ds_task = mo.md(
        """
        ---
        ## **Data Science Task: Building a Forecasting Model**
        You have a tabular dataset, `all_extracted_data.csv`, which contains all of the extracted data for each of the 6 methods. Your goal is to try and accurate predict quarterly revenue values using this historical data.
        First we load our dataset `all_extracted_data.csv` which contains the city's quarterly revenue.
        Use the DataFrame explorer below to get familiar with the data. What differences do you notice?
        """
    )

    options = mo.md(
        "Our dataset has six options for the quarterly revenue data. We need to pick one."
    )

    ai_warning = (
                    mo.md(f"You have selected the **{revenue_selector.value}** dataset.").callout()
                    if not is_ai_source
                    else mo.md(f"""You have selected the **{revenue_selector.value}** dataset, which was extracted using AI.""").callout("warn")
                )


    # display the data
    data_vstack = mo.vstack([ds_task, pgh_revenue_data])
    rdso_2_vstack = mo.vstack([mo.md(rdso_2), reactive_chat]).callout()
    selector_vstack = mo.vstack([revenue_selector, ai_warning])

    mo.vstack([data_vstack, options, rdso_2_vstack, selector_vstack])
    return


@app.cell(hide_code=True)
def _(mo, pgh_revenue_data, revenue_selector):
    rev_description = mo.md("Now you can create a new dataframe, `revenues`, with just the dataset you have selected.")

    # create a copy of just the data we want
    revenues = pgh_revenue_data[['Year-Quarter', revenue_selector.value]].copy()
    revenues = revenues.rename(columns={revenue_selector.value:"revenue"})
    mo.vstack([rev_description, revenues])
    return (revenues,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Now you need to select features for the statistical models. These features will be the inputs to to your modeling function. We are doing a [time-series analysis](https://www.geeksforgeeks.org/machine-learning/time-series-analysis-and-forecasting/) so our features are [lagged values.](https://www.geeksforgeeks.org/machine-learning/what-is-lag-in-time-series-forecasting/) Use the slider below to select how much lag we should lag our features.""")
    return


@app.cell(hide_code=True)
def _(lag_amount, mo):
    mo.vstack([lag_amount, f"You have selected a lag of {lag_amount.value}"])
    return


@app.cell
def _(lag_amount, revenues):
    # add lag value column
    revenues['lag'] = revenues['revenue'].shift(lag_amount.value)
    revenues
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Notice the [missing values](https://www.geeksforgeeks.org/python/how-to-deal-with-missing-values-in-a-timeseries-in-python/) as you increase the lag. Also note, depending on which extraction method column you selected there are missing values as well. Do you want to clean the data and remove rows with missing values?""")
    return


@app.cell(hide_code=True)
def _(mo, remove_missing):
    mo.hstack([
        remove_missing,
        mo.md(
            f"You have decided {'**not**' if not remove_missing.value else ''} to remove missing values."
            f"{' This will feed your model `NULL` values.' if not remove_missing.value else ''}"
        )
    ], justify="start", gap=5)
    return


@app.cell(hide_code=True)
def _(lag_amount, remove_missing, revenues):
    if remove_missing.value:
        # create a new dataframe with no missing values
        clean_revenues = revenues.dropna()
    else:
        #
        clean_revenues = revenues.copy()
        # Add the lag column here to ensure it exists
        clean_revenues['lag'] = clean_revenues['revenue'].shift(lag_amount.value)

    clean_revenues
    return (clean_revenues,)


@app.cell(hide_code=True)
def _(mo, training_percent):
    mo.md(
        f"""
    What percentage of the data do you want to use for [training?](https://www.geeksforgeeks.org/python/training-data-vs-testing-data/#what-is-training-data?)

    {training_percent}

    You have selected {training_percent.value * 100}% of the data for training.
    """
    )
    return


@app.cell
def _(clean_revenues, training_percent):
    # Chronological split
    train_size = int(len(clean_revenues) * training_percent.value)
    train = clean_revenues.iloc[:train_size]
    test = clean_revenues.iloc[train_size:]

    x_train = train[['lag']]
    y_train = train['revenue']
    x_test = test[['lag']]
    y_test = test['revenue']
    return x_test, x_train, y_test, y_train


@app.cell(hide_code=True)
def _(mo, x_test, x_train, y_test, y_train):
    mo.hstack([mo.vstack([mo.md("**X Train**"),x_train,mo.md("**Y Train**"),y_train]),
              mo.vstack([mo.md("**X Test**"),x_test,mo.md("**Y Test**"),y_test]),
              ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## **Forecasting Model Implementation**

    Now you have everything you need to generate the model. As you've made your selections, Marimo has been building the model dynamically behind the scenes. Below are your results alongside a dashboard where you can adjust all parameters in one place if you'd like to make changes.

    ---
    """
    )
    return


@app.cell(hide_code=True)
def _(
    LinearRegression,
    mo,
    root_mean_squared_error,
    x_test,
    x_train,
    y_test,
    y_train,
):
    try:
        # train the model
        model = LinearRegression()
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)

        output = mo.md(
            f"""
            *The model has a Root Mean Square Error (RMSE) of ${root_mean_squared_error(y_test, predictions):,.2f}*

            *What this means:*

            - *On average, your predictions are off by ${root_mean_squared_error(y_test, predictions):,.2f}*
            - *The average actual revenue in your test set is ${y_test.mean():,.2f}*
            - *The RMSE represents {(root_mean_squared_error(y_test, predictions)/y_test.mean()*100):.1f}% of the average revenue*

            *For context:*

            - *68% of predictions should fall within ±${root_mean_squared_error(y_test, predictions):,.2f} of the actual value*
            - *The minimum revenue in your test set is ${y_test.min():,.2f}*
            - *The maximum revenue in your test set is ${y_test.max():,.2f}*
        """
        ).callout('info')
    except ValueError as e:
        output = mo.md(f"""**Your code has an error!**

        ```
        {e}
        ```
        Try adjusting your selections and running the code again.

        """).callout("danger")

    output
    return


@app.cell(hide_code=True)
def _(lag_amount, mo, remove_missing, revenue_selector, training_percent):
    mo.md(
        f"""
    ## Adjust your selections

    Play with the options again and see how the statistical performance changes.

    What combination of choices are most accurate?

    {mo.hstack([revenue_selector, mo.vstack([remove_missing,lag_amount,training_percent])], justify="start", gap=5)}
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        f"""
    ## Communicating Results

    You now have a predictive model for the city's revenue. How would you communicate these results back to Chris?
    """
    )
    return


@app.cell(hide_code=True)
def _(mo, remove_missing, revenue_selector):
    _ai_sources = ["claude", "chatgpt", "docling"]
    is_ai_source = any(value in revenue_selector.value for value in _ai_sources)
    (
        mo.md("You elected not to remove missing values. This broke your model. Try removing those and seeing what you can come up with!").callout('warn')
        if not remove_missing.value
        else mo.md("Nice job! Parsing the data by hand or writing a script to do it for you may take longer, but it ensures that your results are accurate. Now think about how you'll present your findings to your boss.").callout('success')
        if not is_ai_source
        else mo.md(f"""You trained your model using **{revenue_selector.value}**, which is a column from an AI source! You need to think about how you are going to convey the accuracy of the data when you communicate your results back to Chris.""").callout("danger")
    )
    return (is_ai_source,)


@app.cell
def _(mo, rdso_3, reactive_chat):
    mo.vstack([mo.md(rdso_3), reactive_chat]).callout()
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, root_mean_squared_error
    return LinearRegression, mo, pd, root_mean_squared_error


@app.cell
def _(mo, pgh_revenue_data):
    # select the column names that start with "revenue_by"
    revenue_columns = [col for col in pgh_revenue_data.columns if col.lower().startswith('revenue by')]


    # make marimo buttons for each of the values in the revenue_columns list
    revenue_selector = mo.ui.radio(
        options=revenue_columns,
        value=revenue_columns[0],  # sets default value to first column
        label="Select Revenue Column"
    )
    return (revenue_selector,)


@app.cell
def _(mo):
    remove_missing = mo.ui.switch(label="Remove missing values")
    return (remove_missing,)


@app.cell
def _(mo):
    training_percent = mo.ui.slider(start=0.1, stop=0.9, step=0.1, value=0.1, label="Training Set Percentage:")
    return (training_percent,)


@app.cell
def _(mo):
    lag_amount = mo.ui.slider(start=1, stop=5, step=1, value=1, label="Lag Amount:")
    return (lag_amount,)


if __name__ == "__main__":
    app.run()
