from gf3merger import merge

dates_to_be_merged = (
    ("20201003","20201004"),
    ("20201101","20201102"),
    ("20201130","20201201"),
    ("20210225","20210226"),
    ("20221027","20221028"),
    ("20221125","20221126"),
    ("20230122","20230123"),
)

dir_slc = "fakepath"

for parent_date, child_date in dates_to_be_merged:
    merge.GF3Merger(dir_slc=dir_slc, parent_date=parent_date, child_date=child_date).merge()
