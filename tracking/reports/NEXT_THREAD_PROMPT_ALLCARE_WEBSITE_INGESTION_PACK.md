# Next thread — AllCare website ingestion pack

1. Optionally add `--download-assets` to mirror PDFs into `tracking/data/allcare_website_assets/`.
2. Run `python tools/run_business_ingest.py` per manifest entry after content is on disk.
3. Wire review_state tags to ingestion DB.

```bash
python tools/build_allcare_website_ingestion_pack.py --write-reports
```
