async def fifth_back_fucntion(page, FIFTH_BACK_XPATH):
    try:
        back_button = await page.query_selector(FIFTH_BACK_XPATH)
        await back_button.click()
    except Exception as e:
        print(f"Error while going back: {e}")

async def fourth_back_func(page, FOURTH_BACK_XPATH):
    try:
        back_button = await page.query_selector(FOURTH_BACK_XPATH)
        await back_button.click()
    except Exception as e:
        print(f"Error while going back: {e}")

async def third_back_func(page, THIRD_BACK_XPATH):
    try:
        back_button = await page.query_selector(THIRD_BACK_XPATH)
        await back_button.click()
    except Exception as e:
        print(f"Error while going back: {e}")

async def second_back_func(page, SECOND_BACK_XPATH):
    try:
        back_button = await page.query_selector(SECOND_BACK_XPATH)
        await back_button.click()
    except Exception as e:
        print(f"Error while going back: {e}")

async def first_back_func(page, FIRST_BACK_XPATH):
    try:
        back_button = await page.query_selector(FIRST_BACK_XPATH)
        await back_button.click()
        print("Clicked")
    except Exception as e:
        print(f"Error while going back: {e}")
