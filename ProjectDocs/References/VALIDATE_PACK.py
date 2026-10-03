"""Validate actual reference paths and coverage. Never equate coverage with visual completion."""
from pathlib import Path
import json, collections, hashlib, struct

root=Path(__file__).resolve().parent
manifest=json.loads((root/'REFERENCE_MANIFEST.json').read_text())
refs=manifest['references'];assets=manifest['assets']
errors=[]
def check(condition,message):
    if not condition:errors.append(message)
check(len({r['id'] for r in refs})==len(refs),'Duplicate reference IDs')
check(len({r['expected_file'] for r in refs})==len(refs),'Duplicate expected paths')
check(len({a['id'] for a in assets})==len(assets),'Duplicate asset IDs')
for r in refs:
    check((root/r['brief_file']).is_file(),'Missing brief '+r['id'])
    if r['file']:
        f=root/r['file'];check(f.is_file(),'Missing actual image '+r['id'])
        if f.is_file() and f.suffix.lower()=='.png':
            data=f.read_bytes();check(data[:8]==b'\x89PNG\r\n\x1a\n','Invalid PNG signature')
            width,height=struct.unpack('>II',data[16:24])
            check(r['dimensions_px']==[width,height],'Incorrect image dimensions')
            check(r['resolution_compliant']==(max(width,height)>=2048),'Incorrect resolution certification')
    else:
        check(r['visual_complete'] is False,'Missing image falsely marked complete '+r['id'])
        check(r['status']=='PROVISIONAL','Missing image has misleading status '+r['id'])
ids={a['id'] for a in assets}
for pref,n in [('B',20),('O',12),('E',43),('EL',6)]:
    for i in range(1,n+1):check(f'{pref}{i:02}' in ids,f'Missing required {pref}{i:02}')
canon={cid for a in assets for cid in a['canon_ids']}
for i in range(1,46):check(f'C{i:02}' in canon,f'Missing character canon C{i:02}')
categories=collections.Counter(a['category'] for a in assets)
for category,count in [('main_boss',18),('nonboss_encounter',2),('optional_boss',12),('enemy',43),('elite',6),('macroregion',6),('transformation',4),('prop',24),('vfx',15),('material',20)]:
    check(categories[category]==count,'Incorrect coverage count: '+category)
original=root/'01_Nefer/REF_CHR_Nefer_Hero_Locked_Original_v01.png'
check(hashlib.sha256(original.read_bytes()).hexdigest()=='248e1ab5b4be482af957b6ecb26c580666ffe9e99ed3823c54521e36a47f54fe','Nefer master modified')
sourcehash=json.loads((root/'Sources/SOURCE_CHECKSUMS.json').read_text())
for name,expected in sourcehash.items():check(hashlib.sha256((root/'Sources'/name).read_bytes()).hexdigest()==expected,'Source bytes changed '+name)
files=[p for p in root.rglob('*') if p.is_file()]
actual_images=[p for p in files if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp']]
result={'documentation_integrity':'PASS' if not errors else 'FAIL','errors':errors,'files':len(files),'actual_images':len(actual_images),'generated_images':manifest['generated_image_count'],'required_reference_entries':len(refs),'missing_visual_entries':sum(r['file'] is None for r in refs),'resolution_compliant_images':sum(r['resolution_compliant'] is True for r in refs),'visual_completion':'INCOMPLETE','anatomy_and_rig_QA':'DRAFT_VISUAL_REVIEW_ONLY_RIG_UNTESTED','environment_continuity_QA':'NOT_PERFORMED_NO_BLOCKOUT'}
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
