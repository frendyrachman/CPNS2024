from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode (no GUI)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Set up the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to the webpage
driver.get("https://sscasn.bkn.go.id/#daftarFormasi")
print("Page loaded.")
time.sleep(10)  # Wait for the page to load completely

try:
    # Apply filters
    # Jenjang Pendidikan
    jenjang_pendidikan_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='--- Pilih Jenjang Pendidikan ---']"))
    )
    jenjang_pendidikan_input.click()  # Click to open dropdown
    time.sleep(2)  # Wait for the dropdown options to appear

    # Select the appropriate option from the dropdown
    jenjang_pendidikan_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'S-1/Sarjana')]"))
    )
    jenjang_pendidikan_option.click()
    print("Selected 'S-1/Sarjana' for 'Jenjang Pendidikan'")
    time.sleep(2)

    # Program Studi
    program_studi_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='--- Pilih Program Studi ---']"))
    )
    program_studi_input.click()  # Click to open dropdown
    time.sleep(2)  # Wait for the dropdown options to appear

    # Select the appropriate option from the dropdown
    program_studi_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'S-1 TEKNIK FISIKA')]"))
    )
    program_studi_option.click()
    print("Selected 'S-1 FISIKA' for 'Program Studi'")
    time.sleep(2)

    # Jenis Pengadaan
    jenis_pengadaan_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='--- Pilih Jenis Pengadaan ---']"))
    )
    jenis_pengadaan_input.click()  # Click to open dropdown
    time.sleep(2)  # Wait for the dropdown options to appear

    # Select the appropriate option from the dropdown
    jenis_pengadaan_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'CPNS')]"))
    )
    jenis_pengadaan_option.click()
    print("Selected 'CPNS' for 'Jenis Pengadaan'")
    time.sleep(2)

    # Click the "CARI" button to search after setting filters
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'bg-primary') and contains(text(),'CARI')]"))
    )
    search_button.click()
    print("Search button clicked.")
    time.sleep(10)  # Allow time for the table to load after clicking "CARI"

    # Wait for the table to appear
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table-content"))
    )
    print("Table loaded.")

except Exception as e:
    print(f"Error while applying filters or loading table: {e}")
    driver.quit()
    exit()

# Extract table headers
headers = []
try:
    header_elements = driver.find_elements(By.CSS_SELECTOR, ".ant-table-thead th")
    for header in header_elements:
        headers.append(header.text.strip())
    print("Headers extracted:", headers)
except Exception as e:
    print(f"Error extracting headers: {e}")

# Initialize an empty DataFrame to store the scraped data
df = pd.DataFrame(columns=headers)

# Iterate over all pages
while True:
    try:
        # Get table rows
        rows = driver.find_elements(By.CSS_SELECTOR, ".ant-table-tbody tr")
        if not rows:
            print("No data found on this page.")
            break
        
        data = []
        for row in rows:
            row_data = []
            columns = row.find_elements(By.XPATH, './td')
            for column in columns:
                row_data.append(column.text.strip())
            data.append(row_data)

        # Convert to DataFrame and append to the main DataFrame
        df_page = pd.DataFrame(data, columns=headers)
        df = pd.concat([df, df_page], ignore_index=True)
        
        print(f"Page {len(df) // len(rows)} scraped.")

        # Check if the next button is disabled
        next_button = driver.find_element(By.CSS_SELECTOR, ".ant-pagination-next")
        
        if "ant-pagination-disabled" in next_button.get_attribute("class"):
            print("Reached the last page of results.")
            break
        else:
            next_button.click()
            print("Navigating to next page...")
            time.sleep(5)  # Wait for the next page to load

    except Exception as e:
        print(f"Error during pagination or data extraction: {e}")
        break

# Close the driver
driver.quit()

# Check if the DataFrame is not empty before saving
if not df.empty:
    df.to_csv("sscasn_formasi_data_TEKNIK_fisika.csv", index=False)
    print("Data has been successfully saved to sscasn_formasi_data.csv")
else:
    print("No data scraped. The resulting CSV file is empty.")
