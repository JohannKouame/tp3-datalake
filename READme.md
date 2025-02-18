1. **Do this before doing anything**
* Execute the following cmd `docke-compose up -d`to allow the localstack and mangodb on your laptop
* The following cmd to create the tree aws buckets `raw`, `staging`and `curate`:
  * `aws --endpoint-url=http://localhost:4566 s3 mb s3://raw`
  * `aws --endpoint-url=http://localhost:4566 s3 mb s3://staging`
  * `aws --endpoint-url=http://localhost:4566 s3 mb s3://curated`

2. **Load data into raw bucket**

Run the `load_dataset.py`script to do that.

3. **Run mysql locally as staging**

* Run MySQL :`docker run --name mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=staging -p 3306:3306 -d mysql:8.0`
* Install dependency : `pip install mysql-connector-python`



`make manage_buckets empty=False repo=Salesforce/wikitext dataset_name=wikitext-2-raw-v1 bucket_name=raw`