# prospie

prospie is an AI tool to support trusts fundraisers in the third sector. prospie will speed up and improve the trusts prospecting process, saving money for charities and contributing to better fundraiser wellbeing ✨

## Tech Stack and Tools

![image](https://img.shields.io/badge/Supabase-181818?style=for-the-badge&logo=supabase&logoColor=white)
![image](https://img.shields.io/badge/Jupyter-F37626.svg?&style=for-the-badge&logo=Jupyter&logoColor=white)
![image](https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white)
![image](https://img.shields.io/badge/-HuggingFace-FDEE21?style=for-the-badge&logo=HuggingFace&logoColor=black)
![image](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![image](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![image](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![image](https://img.shields.io/badge/Digital_Ocean-0080FF?style=for-the-badge&logo=DigitalOcean&logoColor=white)
![image](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)


## Repo Structure

1. Generates a sample of *n* funders from Charity Commission data (1000 for the prototype)
2. Gets all registered (non-removed) charities from [Charity Commission data](https://register-of-charities.charitycommission.gov.uk/en/register/full-register-download) to serve as potential recipients
3. Builds a database of funders, grants and recipients using the Charity Commission and [360Giving](https://www.360giving.org/explore/technical/api/) APIs
4. Builds a database of grants and recipients using PDFs of official charity accounts
5. Gets information from [The List](https://the-list.uk/) and adds to database
6. Exploratory Data Analysis - explores, cleans and visualises the data   
    6.1. Stores checkpoints locally     
    6.2. Reprocesses PDFs to extract accounts sections using Claude LLM instead of regex
7. Explores the best model and approach for the embeddings    
    7.1. Stores checkpoints locally     
    7.2. Compares embedding models to select the most suitable for the project      
    7.3. Experiments with different approaches to embedding the text to be used in semantic similarity comparisons      
8. Preprocesses data ready for modelling        
    8.1. Stores checkpoints locally     
9. An evaluation form app to gather professional fundraisers' opinions on the alignment of a sample of funder-recipient pairs, to assess the performance of the final prospie app
10. Develops the logic behind the alignment score       
    10.1. Stores checkpoints locally    
    10.2. Develops the scoring logic function-by-function       
    10.3. Tests the scoring logic through iterations by adding and refactoring weightings 
11. A backend to deliver the calculated alignment score of a user's charity and their chosen funder  
12. A frontend to interact with the app     
13. Evaluates the performance of the scoring logic      
    13.1. Stores checkpoints locally        

## How to...

### Build the Database

The database is built in stages by running Python scripts in folders 01-05. Each stage processes and uploads data to your Supabase instance.

#### Prerequisites

- Supabase project with appropriate tables configured [per the schema](https://github.com/lico27/prospie/blob/64276f68aa005a70749cb7eb20427adc115679bc/schema.sql/)
- API keys stored in a `.env` file in the project root:
- `SUPABASE_URL` - your Supabase project URL
- `SUPABASE_KEY` - your Supabase service role key
- `ANTHROPIC_KEY` - Claude API key (for PDF processing in step 04)

#### Steps

1. **Set up Supabase database**
   - Create a new Supabase project
   - Run the `schema.sql` file in your Supabase SQL editor to create all required tables
   - Copy your project URL and service role key to the `.env` file

2. **Generate sample of funders**
   ```bash
   cd 01_sample_generator
   python sample_function.py
   ```
   This generates `sample_charity_numbers.json` with n funders' registered charity numbers stratified by income.

3. **Build recipients table**
   ```bash
   cd 02_recipients_table_builder
   python main.py
   ```
   Downloads all registered charities from Charity Commission and uploads to `recipients` table with classifications and join tables.

4. **Build funders and grants data from APIs**
   ```bash
   cd 03_database_builder_apis
   python main.py
   ```
   Fetches funder data from Charity Commission API and grants from 360Giving API. Uploads to `funders`, `grants`, and related/join tables.

5. **Build grants data from PDF accounts**
   ```bash
   cd 04_database_builder_pdfs
   python main.py
   ```
   Downloads charity accounts PDFs, extracts grants using Claude AI, and uploads to database (skips funders already in 360Giving data).

6. **Add data from The List**
   ```bash
   cd 05_database_builder_csv
   python main.py
   ```
   Processes the latest `the-list-*.csv` file and marks funders on The List.

**Note:** Steps 3-5 can take several hours to complete depending on API rate limits. Progress is saved to the database continuously, so you can stop and resume if needed.

----

### Use the App

The app is deployed at [prospie.app](https://prospie.app).

#### <u>Steps</u>

<strong>1. Enter your details</strong><br>
Enter your charity number. prospie will pull your organisation's information from the Charity Commission.   

<strong>2. Edit your data (recommended)</strong><br>
Whilst you can use the data as-is for a quick assessment, editing it will likely significantly improve the quality of your score:
<ul style="margin-left: 20px; margin-top: 0;">
<li style="margin-bottom: 0.25em;">Be specific – consider focusing on a single project rather than your entire organisation, especially if you work in multiple areas/sectors</li>
<li style="margin-bottom: 0.25em;">Replace generic charity sector language (e.g. "improving wellbeing", "making a difference") with concrete and distinctive keywords – vague language will result in a good alignment with pretty much any funder!</li>
<li style="margin-bottom: 0.25em;">Add or delete keywords and text in any field</li>
</ul>

<strong>3. Enter the funder's charity number</strong><br>
Input the registered charity number of the funder you want to assess alignment with.

<strong>4. Click "Submit" and wait...</strong><br>
prospie calculates your score from lots of different factors, so it can take up to two or three minutes, especially if your funder has a large giving history (fun fact: Esmee Fairbairn Foundation is the biggest, with a whopping 6,987 grants!).

<strong>5. Review your results</strong><br>
Your alignment score will be displayed with clear reasoning behind it. Click the dropdown sections to see detailed breakdowns of how different factors contributed to your score.

#### <u>Please note</u>

<strong>Alignment scores range from 5% to 95%</strong><br>
They will never be 0% or 100%. This reflects the uncertainty of prospecting. prospie can never be 100% certain of an alignment but it can equally never completely rule out the possibility of a match.

<strong>This tool supports your judgment, it doesn't replace it.</strong><br>
prospie is designed to help you make more informed prospecting decisions, not to make those decisions for you.

<strong>The data in this prototype has limitations</strong><br>
The current app only has 996 funders, and many funders have missing or incomplete information.