//first to setup the files

python3 cli.py \
--csv data/raw/milken_spotify.csv \
--config config/config-v2.json \
--out out/plan.json \
--cache out/cache.json \
--mode dry

//next to align those with cadidiates form wiki base

(.venv) rayanhorne@vpn-234 csv_wikibase_pipeline % python -m reconcile.wiki_reconcile_cli export \           
  --cache out/cache.json \           
  --config reconcile/wiki_config.json \
  --out out/reconcile_input.json

//then prep for openrefine

(.venv) rayanhorne@vpn-234 csv_wikibase_pipeline % python -m reconcile.wiki_reconcile_cli export-openrefine \
  --input out/reconcile_input.json \ 
  --csv openrefine.csv \               
  --json openrefine.json        

//then do open refine reconciliation and export out

 python3 -m reconcile.wiki_reconcile_cli2 \
 --input data/orf2.csv \
 --out cache_aligned.json \
 --log wiki_reconcile.log.csv               


//then align that export with the plan

(.venv) rayanhorne@vpn-234 csv_wikibase_pipeline % python -m reconcile.wiki_reconcile_cli align \            
  --plan out/plan.json \             
  --map cache_aligned.json \      
  --out_aligned reconcile/plan_aligned.json \
  --out_unaligned reconcile/plan_unaligned.json \
  --out_status reconcile/plan_status.json
