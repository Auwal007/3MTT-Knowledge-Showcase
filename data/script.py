import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import os

# --- Configuration ---
BASE_URL = "https://ipad.fas.usda.gov/countrysummary/Default.aspx?id=NI"  # Nigeria

# Define the specific crops you want to scrape
TARGET_CROPS = ["Palm Oil", "Rice", "Wheat", "Corn", "Sorghum", "Millet", "Peanut", "Cotton", "Soybean"] # Case-sensitive, ensure these match website text
CSV_FILENAME = "full_nigeria_crop_yield_data_with_headers.csv" # Updated filename
WAIT_TIMEOUT = 25  # Increased timeout for waits, can be adjusted

# --- Setup WebDriver ---
# For easier driver management, consider using webdriver-manager:
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service as ChromeService
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
try:
    driver = webdriver.Chrome() # Ensure chromedriver is in your PATH or specify its location
except Exception as e:
    print(f"Error initializing WebDriver: {e}")
    print("Please ensure Chrome and ChromeDriver are correctly installed and accessible.")
    exit()
    
wait = WebDriverWait(driver, WAIT_TIMEOUT)

# --- Load Existing Data or Initialize ---
if os.path.exists(CSV_FILENAME):
    try:
        df = pd.read_csv(CSV_FILENAME)
        all_data = df.to_dict("records")
        processed_crop_state_pairs = set()
        if 'Crop' in df.columns and 'State' in df.columns:
            df_copy = df[['Crop', 'State']].astype(str) # Ensure strings for comparison
            processed_crop_state_pairs = set(zip(df_copy['Crop'], df_copy['State']))
        print(f"Loaded {len(all_data)} records. Found {len(processed_crop_state_pairs)} processed crop-state pairs from '{CSV_FILENAME}'.")
    except pd.errors.EmptyDataError:
        print(f"'{CSV_FILENAME}' is empty. Starting fresh.")
        all_data = []
        processed_crop_state_pairs = set()
    except Exception as e:
        print(f"Error loading '{CSV_FILENAME}': {e}. Starting fresh.")
        all_data = []
        processed_crop_state_pairs = set()
else:
    all_data = []
    processed_crop_state_pairs = set()
    print(f"No existing data file found at '{CSV_FILENAME}'. Starting fresh.")

# --- Main Script ---
try:
    driver.get(BASE_URL)
    print(f"Navigated to base URL: {BASE_URL}")

    # 1. Get All Available Crop Options from the Dropdown
    crop_dropdown_locator = (By.ID, "DropDownList2")
    available_crop_options_on_page = []
    try:
        wait.until(EC.element_to_be_clickable(crop_dropdown_locator))
        crop_select_element = driver.find_element(*crop_dropdown_locator)
        crop_select_obj = Select(crop_select_element)
        available_crop_options_on_page = [opt.text for opt in crop_select_obj.options if opt.get_attribute("value") and opt.text.strip()]
        if not available_crop_options_on_page:
            print("No crop options found in the dropdown. Exiting.")
            driver.quit()
            exit()
        print(f"Available crops on page: {available_crop_options_on_page}")
    except TimeoutException:
        print("Crop dropdown (DropDownList2) not found or not clickable on initial load. Exiting.")
        driver.quit()
        exit()

    # Filter these options to get only the TARGET_CROPS
    crops_to_process = [crop for crop in available_crop_options_on_page if crop in TARGET_CROPS]

    if not crops_to_process:
        print(f"None of the target crops ({', '.join(TARGET_CROPS)}) were found in the available options on the page.")
        print("Please check the TARGET_CROPS list for exact names (case-sensitive) as they appear on the website.")
        driver.quit()
        exit()
    print(f"Target crops to process: {crops_to_process}")


    # 2. Loop Through Filtered Crops
    for crop_name in crops_to_process:
        print(f"--- Processing Crop: {crop_name} ---")

        current_crop_state_options = []
        try:
            driver.get(BASE_URL)
            wait.until(EC.element_to_be_clickable(crop_dropdown_locator))
            temp_crop_select_el = driver.find_element(*crop_dropdown_locator)
            Select(temp_crop_select_el).select_by_visible_text(crop_name)

            state_dropdown_locator = (By.ID, "SubRegionDropDown")
            wait.until(lambda d: len(Select(d.find_element(*state_dropdown_locator)).options) > 0 and \
                                 "loading" not in Select(d.find_element(*state_dropdown_locator)).options[0].text.lower())
            time.sleep(0.75)

            state_select_el = driver.find_element(*state_dropdown_locator)
            state_select_obj = Select(state_select_el)
            current_crop_state_options = [opt.text for opt in state_select_obj.options if opt.get_attribute("value") and opt.text.strip() and "select" not in opt.text.lower()]

            if not current_crop_state_options:
                print(f"No specific states found for crop '{crop_name}'. Skipping this crop.")
                continue
            print(f"States for '{crop_name}': {current_crop_state_options}")

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Error preparing crop '{crop_name}' or getting its states: {e}. Skipping crop.")
            continue

        # 3. Loop Through States for the Current Crop
        for state_name in current_crop_state_options:
            if (str(crop_name), str(state_name)) in processed_crop_state_pairs:
                print(f"⏩ Skipping already processed: {crop_name} - {state_name}")
                continue

            print(f"  --- Processing State: {state_name} for Crop: {crop_name} ---")
            try:
                driver.get(BASE_URL)

                wait.until(EC.element_to_be_clickable(crop_dropdown_locator))
                c_crop_el = driver.find_element(*crop_dropdown_locator)
                Select(c_crop_el).select_by_visible_text(crop_name)

                state_dropdown_locator = (By.ID, "SubRegionDropDown")
                wait.until(lambda d: len(Select(d.find_element(*state_dropdown_locator)).options) > 0 and \
                                     "loading" not in Select(d.find_element(*state_dropdown_locator)).options[0].text.lower())
                time.sleep(0.75)

                s_state_el = driver.find_element(*state_dropdown_locator)
                Select(s_state_el).select_by_visible_text(state_name)
                print(f"  Selected state: {state_name}")

                view_data_link_locator = (By.ID, "subregionPageLink")
                view_data_link = wait.until(EC.element_to_be_clickable(view_data_link_locator))
                view_data_link.click()

                # Scrape Data from Table (Flexible Column Handling)
                table_locator = (By.ID, "GridView1")
                wait.until(EC.presence_of_element_located(table_locator))

                header_elements = driver.find_elements(By.CSS_SELECTOR, f"#{table_locator[1]} tr th")
                current_table_headers = [th.text.strip() for th in header_elements]
                # *** ADDED LOGGING FOR CLARITY ON HEADERS BEING USED ***
                print(f"    Table headers for {crop_name} - {state_name}: {current_table_headers}")


                data_rows_elements = driver.find_elements(By.CSS_SELECTOR, f"#{table_locator[1]} tr")[1:]

                scraped_data_for_this_entry = False
                for row_el in data_rows_elements:
                    cols = row_el.find_elements(By.TAG_NAME, "td")
                    if not cols: continue

                    row_data_values = [col.text.strip() for col in cols]
                    if len(row_data_values) > 0 and not any(row_data_values): continue
                    if not row_data_values: continue

                    current_row_dict = {"Crop": str(crop_name), "State": str(state_name)}
                    num_data_cells_in_row = len(row_data_values)
                    num_header_texts = len(current_table_headers)

                    for i in range(num_data_cells_in_row):
                        # Use header text if available and not empty, otherwise generate a fallback
                        column_key_base = current_table_headers[i] if i < num_header_texts and current_table_headers[i].strip() else f"UnnamedOrExtraColumn_{i+1}"
                        
                        # Ensure column key is unique for this row's dictionary
                        column_key_final = column_key_base
                        suffix_count = 1
                        while column_key_final in current_row_dict:
                            column_key_final = f"{column_key_base}_{suffix_count}"
                            suffix_count += 1
                        current_row_dict[column_key_final] = row_data_values[i]
                    
                    all_data.append(current_row_dict)
                    scraped_data_for_this_entry = True
                    
                    if num_data_cells_in_row != num_header_texts:
                        print(f"  ℹ️ For {crop_name} - {state_name}: Data cells ({num_data_cells_in_row}) vs Headers ({num_header_texts}) count mismatch.")
                        print(f"     Header Texts Found: {current_table_headers}")
                        print(f"     Row Data Values: {row_data_values}")
                        print(f"     Data captured using available/generic keys.")

                if scraped_data_for_this_entry:
                    print(f"  ✅ Scraped {crop_name} - {state_name}")
                elif not data_rows_elements:
                     print(f"  ℹ️ No data rows found in table for {crop_name} - {state_name}.")
                else:
                     print(f"  ℹ️ Data table present for {crop_name} - {state_name} but no data was appended (all rows might have been empty or filtered).")

                processed_crop_state_pairs.add((str(crop_name), str(state_name)))

            except TimeoutException:
                print(f"  ⚠️ Timeout while processing {crop_name} - {state_name}. Skipping.")
            except NoSuchElementException as e:
                print(f"  ⚠️ Element not found for {crop_name} - {state_name}: {e}. Skipping.")
            except StaleElementReferenceException:
                print(f"  ⚠️ Stale element for {crop_name} - {state_name}. Skipping.")
            except Exception as e:
                print(f"  ❌ An unexpected error for {crop_name} - {state_name}: {e}. Skipping.")
            finally:
                try:
                    if all_data:
                        temp_df = pd.DataFrame(all_data)
                        temp_df.to_csv(CSV_FILENAME, index=False)
                        print(f"  💾 Progress saved ({len(all_data)} total records to '{CSV_FILENAME}').")
                except Exception as e_save:
                    print(f"  Error saving data to CSV: {e_save}")

finally:
    print("🎉 Scraping process completed or terminated.")
    if 'driver' in locals() and driver is not None:
        try:
            driver.quit()
            print("WebDriver closed.")
        except Exception as e_quit:
            print(f"Error closing WebDriver: {e_quit}")