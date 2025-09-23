from gf3merger import merge

dates_to_be_merged = (
    ("20240208","20240209"),
)

dir_slc = "/data/tests/ruikang/cn_xinjiang_glacier_gf3_test/stack/process/S01B01"

for parent_date, child_date in dates_to_be_merged:
    merge.GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date).merge()
