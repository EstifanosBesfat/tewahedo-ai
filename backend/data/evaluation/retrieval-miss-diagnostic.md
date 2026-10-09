# Retrieval miss diagnostic

Read-only analysis of the two Recall@5 misses in the official multilingual-e5-small baseline. No benchmark, unit, embedding, query, or evaluation file was changed. Scores are the `similarity_score` values stored in `retrieval-evaluation-v2.json`. That file does not store a separate distance.

Denominator remains the 14 metric-eligible questions. `direct-01` is not part of this diagnostic.

## direct-05

### A. Question information

1. question_id: `direct-05`
2. exact question: በባልንጀራ ላይ ሐሰት ምስክር ስለመሆን ትእዛዙ ምን ይላል?
3. question_type: direct
4. finalized expected concept: The command against false witness.
5. source document: 10commandments.pdf
6. source pages: 10commandments:chunk-0085 pages [34]; 10commandments:chunk-0089 pages [36]
7. relevant parent chunk IDs: `10commandments:chunk-0085`, `10commandments:chunk-0089`
8. Qualifications preserved by the approved ground truth:
   - The readable Amharic says bearing false witness is lying.
   - The command applies to the speaker and to the person who listens to a false report.
   - The Exodus quotation line is OCR-corrupted and is not a readable quotation. The readable command is «በሐሰት አትመስክር».

Exact Amharic text of each relevant parent chunk:

`10commandments:chunk-0085` pages 34–34

```text
ስምንተኛው ትእዛዝ

«/,ል 2ድራያ ሏሪ በፊፀት ለ4ፉመኃዕአዕር› ዘጸ.20+16፡፡

በሐሰት መመስከር መዋሸት ነው:: በቅዱስ መጽሐ ፍም ስለሐሰት የተነገሩት ቃላት የመዋሸትን አስከፊ ገጽታ የሟያሳዩ ናቸው፡: ስለዚህም ነገር ጠቢቡ ሰሎሞን «ውሸተኛ ከንፈር በእግዚአብሔር ዘንድ አስጸያፊ ነው» በማለት ተና - | ግሯል: ምሳ.12፥22፡:: መዋሸት በአግዚአብሔር ዘንድ የተጠ - ፤!

ላ በመሆኑም ቀደም ብሎ በዘሌዋውያን «እናንተም እርስ ' በርሳችሁ ሐሰት አትነጋገሩ»የሚል ትእዛዝ ተሰጥቶ ነበር: ዘሌ.19፥11፡፡: ይህም በሰዎች ዘንድ ሐሰት መናገር ያለተፈ ቀደ መሆኑን የሚያስገነዝብ ነው:: ከዚህ በመነሣት ሐሰት ወይም ውሸት ምንድነው? ለሚለው ጥያቄ መልስ መስጠቱ አስፈላጊ ነው፡፡ ሐሰት /ውሸት/ የሆነውን አልሆነም፤ ያለሆነ ውን ሆነ ብሎ 'ለሌላው; ሰው መናገር 'ወይም አሉታዊውን አዎንታዊ አዎንታዊውን' ደግሞ አሉታዊ አድርጎ በማቅረብ የተሳሳተ መረጃ መስጠት ማለት ነው:: ሐሰት የእውነት ተቃራኒ ነው::

በዚህ ላይ በመመሥረት ነው መምህረ አሕዛብ የተ ባለው ሐዋርያው ቅዱስ ጳውሎስ ለኤፌሶን ምእመናን በሳ ከው መልእክቱ «ስለዚህ ውሸትን አስወግዳችሁ፥+፥...እያን " ዳንዳችሁ ከባልንጀሮቻችሁ ጋር እውነትን ተነጋገሩ: በማ ለት የመከረው፡: ኤፌ.4፥25፡፡ በዚህ ምንባብም ቢሆን እው ነትን መናገር የክርስትና መሠረት .መሆኑ በግልጥ ነው የተመለከተው፡ ብሌያትም ሆኑ ሐዲሳት ተባብረው ' ሐሰ ትን አውግዘውታል፤ ክፉ ነውና: መዋሸት በሰውም በእግዚአብሔርም ዘንድ መጠላቱ ኃጢአት ስለሆነ ነው፡፡ ውሸት ከፍርሃትና ከደካማ ባሕርይ የሚመነጭ ሊሆን ይችላል፡፡ በራሱ 'የሚተማመንና እውነ ተኛ ሰው አይዋሽም፣ የተሰጠውንም ኃላፊነት በሚገባ ይወ ጣል፡። በራሱ የማይተማመን ደካማና ስነፍ ሰው መዋሸትን የስንፍናው መሸፈኛና ቀላል የመፍትሔ አማራጭ አድርጎና .:0 ..: . ይጠቀምበታል፡፡ አልፎ አልፎም ውሸትን ለቀደመ ሐሰት መሸፈኛ ሲጠቀሙበት የሚታዩም አሉ፡ እንዲህ ዓይነቶቹ ሰዎች ከአንዱ ውሸት ወደሌላው እየቀጠሉ ሲዋሹ ይኖራ ሉ፣ መዋሸታቸውን ለመሸፈን መዋሸትን ለምደዋልና፡፡
```

`10commandments:chunk-0089` pages 36–36

```text
ኪዳን ንግሥቲቱ ኤልዛቤል በኢይዝራኤላዊው በናቡቴ 'ላይ ያቆመቻቸው የሐ ሰት ምስክሮች «ናቡቴ እግዚአብሔርንና ንጉሥን ሰድቦአል ብለው" በናቡቴ ላይ መሰከሩ:: የዚያን ጊዜም ከከተማ አውጥተው እሰኪሞት ድረስ ወገሩች›፡፡ 1ነገ,20፥13፡፡

.።+ ሐዋርያው ቅዱስ ጳውሎስም «በክብርና. በውርደት፥ በክፉ -ዉወሬና በመልካም.-ወሬ ራሳችንን እናማጥናለን፤ አሳቾች ስንባል እውነተኞች ነን»: በማለች የተናገረው በሐዋርያዊ አገልግሎታቸው -ላይ በሐሰት ይናፈስ የነበረውን አሉባልታ የሚመለከት ነበር፡ 2ቆሮ.6+8:: ከዚህም በላይ በቅዱሳን ላይ ስለተነገረው የሐሰት ምስክርነት ሁሉ እንጻፍ ቢባል ጊዜም አይበቃም፡፡ ብዙ ቅዱሳን በሐሰት ምስክርነት የተነሣ ያለ በደላቸው መከራን ተቀብለዋል፤ የነፍስ መሥዋዕትነትም ጭምር ከፍለዋል፡ፎ፡ ለምሳሌ ያህል ቅዱስ አትናቴዎስ ሐዋር ያዊ በዝሙትና በነፍስ ግድያ፤-ሶርያዊው ቅዱስ አብርሃም፤ ታላቁ መቃርዮስ፣ አባ መሪና በዝሙት የተከሰሱት በሐሰት እንደነበር ቅዱሳት ድርሳናት ያስረዳሉ፡፡ እነዚህ ቅዱሳን - አበው በሐሰት ከተከሰሱበት ኃጢአት ነፃ መሆናቸው ተረ ጋግጧል፡፡ -ስለዚህ--እንግዲህ-- በሐሰት ለሟነገር- ክስም ሆነ...

ወሬ ጆሮን ከመስጠት መቆጠብ ለሰው ሁሉ ጠቃሚ ነው::

«በሐሰት አትመስክር» የሚለው ትእዛዝ ዋሽቶ የሚናገረውንና ሐሰተኛ ወሬን የሚሰማውንም ሰው ሁሉ የሚመለከት ነው:: ሐሰት ወሬን የሚሰማና የሚቀበል ሰው ውሽተኛውን የበለጠ እንዲዋሽ ይገፋፋዋልና በኃጢአት ላይ ኃጢአት እንዲሠራ ምክንያት ይሆነዋል፡፡ በዚህ መሠረትም በሐሰት ኃጢአት ተናጋሪውና አድማጩ ሁለቱም ተሳ ታፊዎች ናቸው፡፡ በቅዱስ መጽሐፍ የምናገኘው የመጽሐፍ ቃል የሚያስተምረው ሐሰተኛ ወሬን መስማትና | ማስተ 2ባትም ተገቢ አለመሆኑን ነው: "ምሳ.29፥12፡፡ 'የቤተ-
```

### B. Top-20 retrieval analysis

These are the 20 units returned before parent collapse, in the official ranking.

#### Rank 1: `10commandments:chunk-0013:unit-01`

- parent chunk ID: `10commandments:chunk-0013`
- similarity_score: 0.870754063129425
- page_start: 5
- page_end: 5
- unit token count: 391
- extraction method: ocr
- quality score: 84.57
- ground-truth relevant parent: no

```text
ብሎአል፡፡ የዚህ ዓይነቱ ባልንጀራ ጠቃሚ አይደለም፡፡ ጥፋቴን ዓይቶ ካልነገረኝ እንድስተካከልም ካልመክረኝ ለባዶነቴ ቢሟገትልኝ በመጨረሻ ከውድቀቴ ሊያነሣኝ አይችልምና አይረባኝም፡፡ «እውነተኛ ባልንጀራ መስተዋት ነው» ይባል የለ፡፡

ሰሰው ዝና ተብሎ «እውነት» መሥዋዕት መሆን የለባትም፡: ለጥቅም ተብሎም የሰው ዝና መጠበቅና የሐሰት ተሟጋች መሆን አይገባም፡፤ ስለዚህ ነገርም መጽሐፍ «ኃጥኡን የሚያጸድቅና በጻድቁ ላይ የሚፈርድ ሁለቱ በእግዚአብሔር ዘንድ አስጠያፊዎች ናቸው» ብሏል፡፡ ምሳ 1፲7-15፡፥ አውነትን ስለዝና መለወጥ የእውነት አምላክና እውነት የሆነውን እግዚአብሔርን ክዶ ባለዝና የሆነውን ሰው ማምለክ ነው፡፡ ጌታችን ኢየሱስ ክርስቶስ «እፄ መንገድም አውነት ሕይወትም ነኝነ› ብሏልና እውነትን ሰዝና መለወጥን ጣዖትን ከእግዚአብሔር መጣላት ነው፡፡ ዩሕ. 146: ለአግዚአብሔር የሚገባውን ክብር ለሰው የሚሰጥ ከእግዚአብሔር ይልቅ ሰውን ያመልካል፡፡ እግዚአብሔርን ከቋስደሰት ይልቅ ሰውን በማይገባ ነገር የሚያስደስት የሚያስደስተውን ያመልካል፡፡ ለእግዚአብሔርም ከመታዘዝ ይልቅ ለሰው የሚታቨዝ ሰው የታዘዘለትን ያመልካል፡፡ ቅዱስ ጳውለሮስም «ስውን ወይስ እግዚአብሔርን አሁን አሺ አሰኛለሁን? ወይም ሰውን ደስ ሳሰኝ አፈልጋለሁን? አሁን ሰውን ደስ ባሰኝ የክርስቶስ ባሪያ ባልሆንኩም፡፡› በማለት መናረሩ ለዚሁ ነው፡፡ ገላ, 1-10: | ማንም ሰው ቢሆን የሚያደርገውን ነገር ሁሉ በንጹሕ አአምሮ አግዚአብሔርን ብቻ ለማስደሰት ማድረግ አለበት፡፡
```

#### Rank 2: `10commandments:chunk-0007:unit-01`

- parent chunk ID: `10commandments:chunk-0007`
- similarity_score: 0.8683595657348633
- page_start: 3
- page_end: 3
- unit token count: 227
- extraction method: ocr
- quality score: 82.16
- ground-truth relevant parent: no

```text
የጠቀስናቸው ማስረጃዎች አሠርቱ ትእዛዛት በእግዚአብሔር ጣቶች ተጽፈውና በጽላቱ ተቀርጸው ለሙሴ ከመሰጠታቸው በፊት በሕገ ልቡና በሰው ልጆች አእምሮም የነበሩ በመሆኑ እነዚህን ቀደምት ሕግጋት ልቡና የሚያስታውሱን ናቸው ለማሰለት ይቻላል፡፡

በአጠቃላይ ደግሞ እነዚህን ትእዛዛተ እግዚአብሔር ከእርሱ የተሰጡና በእርሱና በሰው ልጆች መካከል የተደረጉ ኪዳናት መሆናቸውን እያሰቡ የፈጸሟቸውና የተመሩባቸው በረከትን ከአግዚአብሔር ዘንድ የሚያገኙ ሲሆን የናቁአቸውን የተውአቸው ደግሞ መርገምን ይቀበላሉ፡። እነዚህን ትእዛዛተ እግዚአብሔርን ለመፈጸምና የእግዚአብሐርን የጸጋ ስጦታም ሰመቀበል ደግሞ እያንዳንዳቸውን በጥልቀት መመልከትና ማጥናት ተገቢ ነውር በሚቀጥለው እትም የመጀመሪያውን ትእዛዝ ይዘን እንቀርባለን: የአግዚአብሔርን ቸርነት የድንግል ማርያም አማላጅነት ክሁላችን ጋር ይሁን አሜን:
```

#### Rank 3: `10commandments:chunk-0086:unit-02`

- parent chunk ID: `10commandments:chunk-0086`
- similarity_score: 0.8675439953804016
- page_start: 35
- page_end: 35
- unit token count: 399
- extraction method: ocr
- quality score: 80.54
- ground-truth relevant parent: no

```text
ዋሸ ያመነውን ተነሳሒ የሚያናዝዘው ካህን ለመዋሸት የገፋ - ፋው ምን እንደሆነ ይነግረው ዘንድ ሊጠይቀው ይባባል፤ ከውሸት በስተጀርባ ሌላ ኃጢአት ሳይኖር አይቀርምና: ሐሰትን ወደዓለም ያስገባው የመጀሪያው ውሸተኛ ጠላ ታችን ዲያብሎስ ነው: እርሱ በሥጋ ከይሲ በእባብ ተሰውሮ የመጀመሪያ ወላጆቻችንን አዳምንና -ሔዋንን «ሞትን አትሞቱ ም» በማለት በሐሰት በተናገራቸው ጊዜ "ዋሸ፡፡ ዝፍ.3፥4፡፥ ለዚህ ውሸት ያነሣሣውም ክፋቱና እነርሱን ለማጥፋት የነበረው ፍላጎቱ ነው።፡ እግዚአብሔርም ስለዚህ ክፉ ጠሳታችን ሲናገር «እርሱ ...ሐሰተኛ የሐሰትም አባት ነውና:> ማለቱን በወንጌል ተጽፎ እናገኘዋለን፡፡ ዮሐ.8፥44፡፡ እነዚህ ምንባ ባት ሐሰተኛ ሰው በግብሩ የዲያብሎስ ልጅ መሆኑን ያስተምሩናል፡፡ ! | ሐሰት ቀጥተኛ ወይም ተዘዋዋሪ ሊሆን ይችላል፡፡ የሐ' ሰት መልእክትን የሚያስተላልፍ ሰው ሁሉ በተዘዋዋሪ ስለ.

ሚዋሽና' የውሸትም ተባባሪ ስለሆነ ሐሰተኛ ነው:: አንዳንድ የዋህ ሰዎች መድኃኒታችን «እንደ እባብ ብልህ አንደ ርግብ" የዋህ ሁኑ» . ያለውን.. በመዘንጋት የሰሙትን ሁሉ እውነት መሆኑን ሳያረጋግጡ ,መልሰው በማውራት የሐሰት ተባባ ሪኖ ሐሰተኞች ይሆናሉ፡፥ የክርስቲያኖች የዋህነት -ግን በማ- ስተዋልና በጥበብ ሳይ የተመሠረተ መሆን ይገባዋል፡ ሳያረ ጋግጡ- መናገር ሳያውቁ ' መመስከር በተለይ ከክርስቲያኖች የሚጠበቅ አይደለም፡፡
```

#### Rank 4: `10commandments:chunk-0012:unit-01`

- parent chunk ID: `10commandments:chunk-0012`
- similarity_score: 0.8668813705444336
- page_start: 5
- page_end: 5
- unit token count: 251
- extraction method: ocr
- quality score: 84.57
- ground-truth relevant parent: no

```text
5. ዝናን ማምለክ

አንዳንድ ሰዎች በሚገባ ወይም በማይገባ ነገር ለዝናቸው ወይም ለሚያውቁት ሰው ዝና ሲሟገቱ ይታያሉ፡፡

የራሳቸውን ወይም የሚሟገቱለትን ሰው ስህተት በመሸፈን ጥፋቱን ከቤተ ክርስቲያን ከሕዝብ ወይም ከመንግሥት በላይ አድርገው ዝናውን ለመጠበቅ ይጥራሉ፡ፎ መሳሳታቸውን ወይም የሚሟገቱለት ሰወ ስህተት መፈጸሙን ቢያውቁም ስለምድራዊ ዝና ሲሉ እውነትን ይደብቋታል፡፡ ይህ ደግሞ ለዝና መዛትና ዝናን ማምለክ ነው፡ ጸሐፊው ስሰዝና የሚሟገቱትን አስመልክቶ «የባልንጀራ ዓይን ለስህተት የተደፈነች ናት፡ፁ፡: የጠሳት ዓይን ግን አያንዳንዱን ጥፋት ትገልጣለች» ብሎአል፡፡ የዚህ ዓይነቱ ባልንጀራ ጠቃሚ አይደለም፡፡ ጥፋቴን ዓይቶ ካልነገረኝ እንድስተካከልም ካልመክረኝ ለባዶነቴ ቢሟገትልኝ በመጨረሻ ከውድቀቴ ሊያነሣኝ አይችልምና አይረባኝም፡፡ «እውነተኛ ባልንጀራ መስተዋት ነው» ይባል የለ፡፡
```

#### Rank 5: `10commandments:chunk-0087:unit-01`

- parent chunk ID: `10commandments:chunk-0087`
- similarity_score: 0.8665153980255127
- page_start: 35
- page_end: 35
- unit token count: 388
- extraction method: ocr
- quality score: 80.54
- ground-truth relevant parent: no

```text
,መልሰው በማውራት የሐሰት ተባባ ሪኖ ሐሰተኞች ይሆናሉ፡፥ የክርስቲያኖች የዋህነት -ግን በማ- ስተዋልና በጥበብ ሳይ የተመሠረተ መሆን ይገባዋል፡ ሳያረ ጋግጡ- መናገር ሳያውቁ ' መመስከር በተለይ ከክርስቲያኖች የሚጠበቅ አይደለም፡፡

ዓለማችን እውነት 'ም ሐሰትም፣ እውነተኛም ሐሰተኛም - የመላባት በመሆኑዋ በው ስጧ የሟዊር ሰው ሁሉ የሚሰማውን - በደፈናው ከማመን” አስቀድሞ ' , መመርመርና - እውነተኛውን ነገር ማረጋገጥ ግዴታው 'ሊሆን ይገባል: በብሉይም ሆነ በሐ ዲስ «ኪዳን: ነገር ሁሉ በምስክር የተረጋገጠ ሲሆን እንደሚጸና መነገሩ ስለዚህ ነው፡፡ ዝዳ.17፥6፡፡:- ማቴ.18፥16፡:- 2ቆሮ: 13+1፡፡ በዚሁ የተነሣም በቅዱስ መጽሐፍ ውስጥ «ነገር ሁሉ በሁለት ወይም”-.በሦስት- ምስክር. ይጸናል» የሚለው ቃል በተደጋጋሚ ተጽፎ 'እናገኝዋለን፡፡ ስለአንድ ነገር ምስክርነቱን የሰጠ ወይም የሰማውን ለሌላ ሰው የተናገረ ሰው ስለነገሩ እውነቱን ላያውቀው ሰ ሰለሚቸል፣' ስለተ ናገረው ነገር የተረ ጋገጠ "ፅው ቀት ላይኖረው ስለሚችል፣ ነገሩም የተጋነነ. ሊሆን ስለሚችል፣ የተሳሳት ነገር ሰምቶ ሊሆን ስለሚችል፣ ስለሰ ማው ነገር የማይታመን 'ወይም. አጠራጣሪ መረጃ -ሊያገኝ .- ስለሟችል፣፤ በግል ምክንያት የሰውን ዝና'ለመጉዳት ብሎሊ. .

ያደርገው -ስለሚችልኖ በመሳሰሉት ምክንያቶች እንዶ 'እርግጠ ኛ. ምስክር ሊቆጠር አይገባም፡፡ .
```

#### Rank 6: `10commandments:chunk-0093:unit-01`

- parent chunk ID: `10commandments:chunk-0093`
- similarity_score: 0.8658826947212219
- page_start: 38
- page_end: 38
- unit token count: 423
- extraction method: ocr
- quality score: 83.66
- ground-truth relevant parent: no

```text
ብቻ አጉልቶ በማ ሳየት ሌሎች ስለእርሱ ያሳቸውን አመለካከት ለመለወጥ መሞከር ግማሽ እውነት በመሆኑ እንደሐሰት የሚቆጠርና በኃጢአትነቱም የሚያስጠይቅ ነው: ሐሰት የተሰኘበት ምክንያትም ስለ ሰውየው የተሳሳተ መረጃ መስጠት ስለሆነ ነው::

ሐሰተኛ ሰው በሕብረተሰቡ መካከል ያለው ሥፍራ የተናገረው ነገር ተአማኒ እንዳይሆን ያደርገዋል፡፡ እንዲህ ያለው ሰው የሚናገረው ሐሰት አስጠያፊ ነው: ስለሆነም ሐ ሰትን የሚናገረው ሰው ደረጃው ከፍ ያለ መሆኑ የተናገ ረውን ሐሰት የበለጠ አስጠያፊ ያደርገዋል፡፡ በዚሁ ኣንፃር ሐ ሰተኛውን ወሬ የተናገረው ሰው ሥልጣንና ደረጃ "ሐሰትን ኣስጠያፊ ያደርገዋል፡ ለማንኛውም ' ተራ ሰው የተነገረና ለባለሥልጣን ወይም ለመንፈሳዊ አባት የተነገረ ሐሰት የሚ መዘንበት ሚዛን እኩል. አይደለም፡፡ ለምሳሌ ያህልም የዮሴፍ ወንድሞች ለአባታቸው እንደዋሹት፣ አንድ ሰውም ለንሰሐ.

-. አባቱ እንደሚዋሽ፤ ሐናንያና ሰሏራ መንፈስ ቅዱስን እንደ ዋሹና እግዚአብሔር እንደቀጣቸው: የሕሐዋ.5፥3-4፡፡

| በሕዝቡ መካከል ከያዙት መንፈሳዊ ሥልጣንና ሥፍራ የቱነሣ ሕዝቡን የሚያስቱትን ሐሰተኞች ነቢ ያት፣ ሐሰተኞች ክርስቶሶች፣ እግዚአብሔር ያልነገራቸውን ነገርን የሚሉ ሐሰተኞች መምህራንንና የመሳሰሉትን ሁሉ እግዚአብሔር «አኔም ሳልናገር:- እግዚአብሔር እንዲህ ብሏል ስትሉ፥ ከንቱ ራእይን ያያችሁ፣ ውሸተኛንም ምዋ ርት. የተናገራችሁ አይደላችሁምን? በማለት ስለጥፋታቸው ነቅፎአቸዋል፡፡- ሕዝ.13፥7፡፡- ስለሐሰተኞች- ነቢያት ደግሞ «በስሜ ሐሰትን የሚናገሩትን የነቢያትን ነገር ሰምቻለሁ፡> በማለት ቅሬታውን ገልጧል፡- ኤር.23፥25፡.- ሕዝቡ
```

#### Rank 7: `10commandments:chunk-0088:unit-01`

- parent chunk ID: `10commandments:chunk-0088`
- similarity_score: 0.8644039630889893
- page_start: 36
- page_end: 36
- unit token count: 386
- extraction method: ocr
- quality score: 81.01
- ground-truth relevant parent: no

```text
' ይነቱ ተግባር በጥንቃቄ ላይ ካልተመሠረተ እውነተኛውንና . ጻድቁን ወደመኮነን ሊያደርስ ይችላል፤ በመጽሐፍም «በድፍ ፡ ረትና በትዕቢት በመናቅም በጻድቅ /በእውነተኛው'፤ ላይ ፡ የሚናገሩ የሽንገላ ከንፈሮች ድዳ ይሁኑ፡:» የተባለው ሳይረጋ ገጥ ስለሚነገር ነገር አደገኛነት ለማመልከት ነው:: መዝ. 30፥18::: ይህም የተባለበት ምክንያት ብዙዎች የአይሁድ

ሊቃነ ካህናት ' እንደአደረጉት ሁሉ' በቅዱሳን ላይ በሐሰት ስለሚመሰክሩ ነው፡፡ እነዚህ በጌታችን በኢየሱስ ክርስቶስ ላይ . የሐሰት ምስክር ይፈልጉ ነበርና» ማቴ.26 ፥59፡፡

- በቅዱሳን ላይ በሐሰት መመስከር .-በመጽሐፍ እንደተመዘገበው ቅዱስ እስጢፋኖስን አይ ሁድ ‹ሊገድሉት በፈለጉ ጊዜ ብዙ ሰዎች በሐሰት መስክ ረውበት ነበር፡ በሐሰት ቃላቸው «ይህ ሰው በዚህ በተቀ ደሰው ስፍራ በሕግም ላይ የስድብን ነገር ለመናገር አይ ተውም» በማለት እነርሱን ትክክለኛ፤ እርሱን ደግሞ ተሳዳቢ ና ሕግን ተላሳፊ አድርገው .በመናገር . መስክረውበት ነበር፡: የሐዋ.6፥13:-: ቀደም ብሎም በብሉይ ኪዳን ንግሥቲቱ ኤልዛቤል በኢይዝራኤላዊው በናቡቴ 'ላይ ያቆመቻቸው የሐ ሰት ምስክሮች «ናቡቴ እግዚአብሔርንና ንጉሥን ሰድቦአል ብለው" በናቡቴ ላይ መሰከሩ:: የዚያን ጊዜም ከከተማ አውጥተው እሰኪሞት ድረስ ወገሩች›፡፡ 1ነገ,20፥13፡፡
```

#### Rank 8: `10commandments:chunk-0089:unit-02`

- parent chunk ID: `10commandments:chunk-0089`
- similarity_score: 0.8643059730529785
- page_start: 36
- page_end: 36
- unit token count: 150
- extraction method: ocr
- quality score: 81.01
- ground-truth relevant parent: yes

```text
«በሐሰት አትመስክር» የሚለው ትእዛዝ ዋሽቶ የሚናገረውንና ሐሰተኛ ወሬን የሚሰማውንም ሰው ሁሉ የሚመለከት ነው:: ሐሰት ወሬን የሚሰማና የሚቀበል ሰው ውሽተኛውን የበለጠ እንዲዋሽ ይገፋፋዋልና በኃጢአት ላይ ኃጢአት እንዲሠራ ምክንያት ይሆነዋል፡፡ በዚህ መሠረትም በሐሰት ኃጢአት ተናጋሪውና አድማጩ ሁለቱም ተሳ ታፊዎች ናቸው፡፡ በቅዱስ መጽሐፍ የምናገኘው የመጽሐፍ ቃል የሚያስተምረው ሐሰተኛ ወሬን መስማትና | ማስተ 2ባትም ተገቢ አለመሆኑን ነው: "ምሳ.29፥12፡፡ 'የቤተ-
```

#### Rank 9: `10commandments:chunk-0054:unit-01`

- parent chunk ID: `10commandments:chunk-0054`
- similarity_score: 0.862360954284668
- page_start: 20
- page_end: 20
- unit token count: 269
- extraction method: ocr
- quality score: 82.65
- ground-truth relevant parent: no

```text
የስው ዘር እንዳይፈጠር የተደረገ የረቀቀ የግድያ ወንጀል ከመሆኑ ' አትግደል ለሚለው ትእዛዝ ተቃራኒ ነው::

በሌላም .በኩል ያልተወለደውንና ወደፊትም በሕ ይወት የመኖር .እድል ያለውን ፅንስ የማኖሩም ሆነ የመግደሉ ሥልጣን የእግዚአብሔር ሆኖ ሳለ በውርጃ እንዲ ወጣ ማድረግና ማስወገድ ራሱ የአምስተኛው ትእዛዝ ተቃራኒና 'የግድያ' ወንጀልም ነው:: በሕገ እግዚአብሔር አትግደል ከመባሉም ሌላ በወንጀለኛ መቅጫ ሕግም የዚ 'ህን ተግባር' ፈጻሚዎች ወንጀለኞች የሚያደርጋቸው ድን ኃጌ አለ:: «በእግዚአብሔር ፈቃድ ከተፀነሰ በኋላ ሕልው ናው በሰው ባልተፈለገ ፅንስ ላይ በሚደረግ የማስወረድ ወን ጀል 'የተሳተፉት ሁሉ 'በምድራዊ ሕግም በወንጀል በእግዚ አብሔር ሕግም በኃጢአት ተጠያቂዎች ናቸው:፥ ውርጃን በማ ንኛውም መንገድ የሚያግዙ ሰዎች የግድያ ወንጀል ተ ባ ባሪ መሆናቸውን ማወቅና ከዚህ ኃጢአት'፡ መከልከል ይኖርባቸዋል፡፡
```

#### Rank 10: `10commandments:chunk-0111:unit-01`

- parent chunk ID: `10commandments:chunk-0111`
- similarity_score: 0.8621425032615662
- page_start: 46
- page_end: 46
- unit token count: 412
- extraction method: ocr
- quality score: 83.12
- ground-truth relevant parent: no

```text
ከመሥዋዕት፥ ማዳመጥም የአውራ በግ ስብ ከማቅረብ - ይበልጣል:> ያለው የእግዚአብሔርን ሕግ መፈጸም የከበረ መንፈሳዊ ዋጋ ያለውና እግዚአብሔርንም የሚያስደስት መሆኑን ለማስረዳት ነው: 1ሳሙ.15፥22፡ መድኃኒታችን ኢየሱስ ክርስቶስም - በመዋዕለ ትም ሀርቱ ባልንጀራን እንደመውደድ አግዚአብሔርን የሚያ ፡ ስደስተው ነገር - የሌለ መሆኑን ሲገልጥ «በፍጹም ልብ በፍጹም አእምሮም በፍጹም ነፍስም በፍጹም ኃይልም እርሱን መውደድ እግዚአብሔርን-፥ባልንጀራንም እንደራስ መውደድ በሙሉ ከሚቃጠል መሥዋዕትና ከሌላው መሥዋዕት ሁሉ የሚበልጥ ነው» በማለት አስተምሯል፡፡

ማር.12-+33:: | | እግዚአብሔርን መውደድና ባልንጀራንም እንደራስ መውደድ የሕግጋት ማሠሪያ ነው፤ ሕግጋትና ትእዛዛት ሁሉ በእነዚህ በሁለቱ ይጠቃለላሉ፡፡ ቅዱሳት መጻሕፍትም ይህንኑ ያረጋግጡልናል: ከነዚህም ማረጋገጫዎች መካከል ጌታችን ኢየሱስ ክርስቶስ ትእዛዛት ሁሉ እግዚአብሔርን በማ ፍቀርና ባልንጀራን እንደራስ በመውደድ የሚጠቃለሉ መሆኑን ከገለጸ በኋላ «ኦሪትና ነቢያት በእነዚህ በሁለቱ ትእዛዛት ጸኑ» በማለት የተናገረው. አንዱ ነው::

ማቴ.22-37-40:፡፡ | ቅዱስ ጳውሎስም በዚህ ቃለ ወንጌል መሠረት ለሮሜ ክርስቲያኖች በጻፈው መልእክት «አርስ በርሳችሁ ከመዋደድ በቀር ለማንም ዕዳ አይኑርባችሁ፥ ሌላውን የሚወድ ሕግን ፈጽሞታልና፡። አታመንዝር+ አትግደል፥ አትስረቅ፥ በውሸት አትመስክር+ አትመኝ የሚለው ከሌሳ
```

#### Rank 11: `10commandments:chunk-0081:unit-01`

- parent chunk ID: `10commandments:chunk-0081`
- similarity_score: 0.8595633506774902
- page_start: 32
- page_end: 32
- unit token count: 396
- extraction method: ocr
- quality score: 83.52
- ground-truth relevant parent: no

```text
ከሥራ መቅረት ወዘተ ከመለመዱ የተነማ ብዙዎች ኃጢአት ሳይመስላቸው የሚፈጽሙት ነው፡ፎ፡ እንዲሁም አንድ የመሥሪያ ቤቱ የፅቃ ግዚ ክፍል ሠራተኛ የሆነ ሰው አሮጌ ቢገዛ ወይም ያልተገዛበትን ዋጋ በደረሰኝ ቢያሠራ የሰረቀ አይመስለውም፡፡

ወደ ነጋዴውም ኀብረተሰብ ስንገባ የባሰ አንጂ የተሻለ ነገር አናገኝም፡፡ በሜትርና በሚዛን ከማጭበርበር አልፈው ብዙ ሲስሩ እናገኛቸዋለን፡፡ እህል ነጋዴው አፈርና ገለባ ይደባልቅበታል ኪሎ እነዲያነሣም ውኃ ያርከፈክፍበታል፡፡ በርበሬ ነጋዴው ሸክላ ቅቤ ነጋዴው ደግሞ ሙዝ ድንች ይቀላቅላል።፡- አሮጌውን እንደ አዲስ የሚሸጠውን አጅ መንሻ መስጠት ሕጋዊ ያልሆነውን ንግድ የሚያካሂደውን ቤት ይቁጠረው፡: ይህ ሁሉ የራስ ያልሆነው አለአግባብ መውሰድ ነውና ስርቆት ነው፡፡

ለመሆኑ ሰዎች ለምን ይሰርቃሉ? አንድ ሰው ወደ ስርቆት ኃጢአት የሚገፋፉት ነገሮች/ ምንጮች/ ምንድን ናቸውን 1. ምኞት:- ያልተሰጠንና የራስ ያልሆነውን ነገር ወይም ያዩትን ሁሉ ለሪስ እንዲሆን መመኘት ወደ ስርቆት ያመራል፡፡

አንድ ገንዘብ የሌለው ሰው ገንዘብ ሳይኖረው ብዙ ነገሮች እንዲያሟሉለት ቁጭ ብሎ ማይሰራ የሚመኝ ከሆነ የግድ ያንን የፈለገውን ነገር ለማሟላት ወደ ሰርቆት ሊያመራ ይችላል፡፡ ፊልጵ «11 2. ችግር :- አንዳንድ ሰዎች ሳይወዱ በችግር ምክንያት ሲሰርቁ ይችላሉ፡ ለምን እንደሠረቁም ሲጠየቁ ቸግሮኝ ነው ይላሉ፡። ይሁን አንጂ ቢቸግርም ጠይቆ /ለምኖ/ መውሰድ /ማግኘት/ ሲቻል መስረቅ አይገባም፡:
```

#### Rank 12: `10commandments:chunk-0076:unit-01`

- parent chunk ID: `10commandments:chunk-0076`
- similarity_score: 0.8583327531814575
- page_start: 30
- page_end: 30
- unit token count: 408
- extraction method: ocr
- quality score: 84.24
- ground-truth relevant parent: no

```text
ሰባተኛው ትእዛዝ

አትስረቅ አግዚአብሔር አስቀድሞ የሰው ልጆች ትአዛዙን እንዳይተላለፉ ካስቀመጠላቸው ሕግጋት መካከል አንዱ ነው፡: እግዚአብሔር ያዘዘን በወዛችን ጥረን ግረን አንድንበላ እንጂ የሌሳውን /የሰውንም ሆነ የአግዚአብሔርን/ እየሰረቅን እንድንበላ አይደለም፡፥ ሽፍ 3፡፲9፡ ለዚህም ነው "አትስረቅ" ሲል ቃሉን ያወጀው፡፡ ይህ ትእዛዝ በጽሑፍ ከመሰጠቱም በፊት ስርቆት ኃጢአት መሆኑ በሕገ ልቡና ይታወቅ ነበር፡፥ ሽፍ 3፲፣ 3ዐ፡፡ - ስርቆትና ሌብነት ተመሳሳይ ሲሆኑ ስርቆት ሰፋ ይላል፡፡ ሌብነት የራስ ያልሆነን ንብረት ባለቤቱ ሳያይ ተደብቆ ያለ ባለቤቱ ፈቃድ መውሰድ ሲሆን ስርቆት ግን ከዚህ በተጨማሪም መስጠት የሚገባን አለመስጠትን ወይም ማድረግ የሚገባን አለማድረግ ያጠቃልላል፡፡ ለምሳሌ አንድ ሰው አሥራት ማውጣት ሲገባው ባያወጣ እግዚአብሐር እንደሰረቀ ይቆጠራል፡፡ ': ሚል3፡7፡፡ ' ስርቆት ከመፈጸሙ በፊትም ሆነ ከተፈጸመ በኋላ ከሌሎች ኃጢአቶች ጋር ይያያዛል፡፡ -፡፡ ከመፈጸሙ በፊት "የባልንጀራህን ቤት አትመኝ" ከሚለው ጋር ከተፈጸመ በኋላ ደግሞ "የአምላክህን ስም በክንቱ አትጥራ" ከሚለው እና "በሐሰት አትናገር" ከሚለው ጋር ይገናኛል፡፡ ምክንያቱም አንድ ሰው የባልጀራውን ንብረት ሰው አየኝ አላየኝ እያለ የሚሰርቀው የእግዚአብሔርን ቃል ተላልፎ በሚያዝበት ጊዜ "ፈጽሞ አላየሁም" ብሎ ይዋሻል ሐሰት ይናገራል፡፡ - ነገሩንም እውነት ለማስመሰል መሐላ እየደረደረ የእግዚአብሔርን ስም በከንቱ ይጠራል፡፡
```

#### Rank 13: `10commandments:chunk-0085:unit-01`

- parent chunk ID: `10commandments:chunk-0085`
- similarity_score: 0.8582947850227356
- page_start: 34
- page_end: 34
- unit token count: 293
- extraction method: ocr
- quality score: 80.76
- ground-truth relevant parent: yes

```text
ስምንተኛው ትእዛዝ

«/,ል 2ድራያ ሏሪ በፊፀት ለ4ፉመኃዕአዕር› ዘጸ.20+16፡፡

በሐሰት መመስከር መዋሸት ነው:: በቅዱስ መጽሐ ፍም ስለሐሰት የተነገሩት ቃላት የመዋሸትን አስከፊ ገጽታ የሟያሳዩ ናቸው፡: ስለዚህም ነገር ጠቢቡ ሰሎሞን «ውሸተኛ ከንፈር በእግዚአብሔር ዘንድ አስጸያፊ ነው» በማለት ተና - | ግሯል: ምሳ.12፥22፡:: መዋሸት በአግዚአብሔር ዘንድ የተጠ - ፤!

ላ በመሆኑም ቀደም ብሎ በዘሌዋውያን «እናንተም እርስ ' በርሳችሁ ሐሰት አትነጋገሩ»የሚል ትእዛዝ ተሰጥቶ ነበር: ዘሌ.19፥11፡፡: ይህም በሰዎች ዘንድ ሐሰት መናገር ያለተፈ ቀደ መሆኑን የሚያስገነዝብ ነው:: ከዚህ በመነሣት ሐሰት ወይም ውሸት ምንድነው? ለሚለው ጥያቄ መልስ መስጠቱ አስፈላጊ ነው፡፡ ሐሰት /ውሸት/ የሆነውን አልሆነም፤ ያለሆነ ውን ሆነ ብሎ 'ለሌላው; ሰው መናገር 'ወይም አሉታዊውን አዎንታዊ አዎንታዊውን' ደግሞ አሉታዊ አድርጎ በማቅረብ የተሳሳተ መረጃ መስጠት ማለት ነው:: ሐሰት የእውነት ተቃራኒ ነው::
```

#### Rank 14: `10commandments:chunk-0089:unit-01`

- parent chunk ID: `10commandments:chunk-0089`
- similarity_score: 0.8582144975662231
- page_start: 36
- page_end: 36
- unit token count: 372
- extraction method: ocr
- quality score: 81.01
- ground-truth relevant parent: yes

```text
ኪዳን ንግሥቲቱ ኤልዛቤል በኢይዝራኤላዊው በናቡቴ 'ላይ ያቆመቻቸው የሐ ሰት ምስክሮች «ናቡቴ እግዚአብሔርንና ንጉሥን ሰድቦአል ብለው" በናቡቴ ላይ መሰከሩ:: የዚያን ጊዜም ከከተማ አውጥተው እሰኪሞት ድረስ ወገሩች›፡፡ 1ነገ,20፥13፡፡

.።+ ሐዋርያው ቅዱስ ጳውሎስም «በክብርና. በውርደት፥ በክፉ -ዉወሬና በመልካም.-ወሬ ራሳችንን እናማጥናለን፤ አሳቾች ስንባል እውነተኞች ነን»: በማለች የተናገረው በሐዋርያዊ አገልግሎታቸው -ላይ በሐሰት ይናፈስ የነበረውን አሉባልታ የሚመለከት ነበር፡ 2ቆሮ.6+8:: ከዚህም በላይ በቅዱሳን ላይ ስለተነገረው የሐሰት ምስክርነት ሁሉ እንጻፍ ቢባል ጊዜም አይበቃም፡፡ ብዙ ቅዱሳን በሐሰት ምስክርነት የተነሣ ያለ በደላቸው መከራን ተቀብለዋል፤ የነፍስ መሥዋዕትነትም ጭምር ከፍለዋል፡ፎ፡ ለምሳሌ ያህል ቅዱስ አትናቴዎስ ሐዋር ያዊ በዝሙትና በነፍስ ግድያ፤-ሶርያዊው ቅዱስ አብርሃም፤ ታላቁ መቃርዮስ፣ አባ መሪና በዝሙት የተከሰሱት በሐሰት እንደነበር ቅዱሳት ድርሳናት ያስረዳሉ፡፡ እነዚህ ቅዱሳን - አበው በሐሰት ከተከሰሱበት ኃጢአት ነፃ መሆናቸው ተረ ጋግጧል፡፡ -ስለዚህ--እንግዲህ-- በሐሰት ለሟነገር- ክስም ሆነ...

ወሬ ጆሮን ከመስጠት መቆጠብ ለሰው ሁሉ ጠቃሚ ነው::
```

#### Rank 15: `10commandments:chunk-0107:unit-01`

- parent chunk ID: `10commandments:chunk-0107`
- similarity_score: 0.8580265045166016
- page_start: 43
- page_end: 44
- unit token count: 379
- extraction method: ocr
- quality score: 80.7
- ground-truth relevant parent: no

```text
ቅዱሳት መጻሕፍት ያሰተ ምራሉ፡፡ ለምሳሌ ጠቢቡ ሰሎሞን «ባልንጀራውን የሚንቅ ይበድላል» - በማለት የተናገረው ሰውን መናቅ ኃጢኣት .ፒ ከመሆኑም በላይ በእግዚአ ብሔር ፊት የሚያስጠይቅ መሆኑን የሚያስረዳ ነው: ምሳ 14+21፡፡

በቅዱስ ወንጌልም እንደተጻፈው የዘለዓለምን ሕይ ወት ለመውረስ ምን ማድረግ እንደሟገባ- መድኃኒታችን :ኢየሱስ - ክርስቶስን. ለጠየቀው ጎልማሳ የተሰጠው መልስ ትአዛዛትን -እንዲፈጽም ነበር፡ -ትእዛዛቱ እንዲዘረዘሩለት ‹በመጠየቅ ጌታችን ኢየሱስ ክርስቶስ «አትግደል፣ አታ ,መንዝርሂ አትስረቅ፤ በሐሰት አትመስክር፣ - እናትህንና አባትህን አክብር» በማለት ከዘረዘረለት በኋላ «ባልንጀራህን

ላካዊ ሕግና በተለይም ደግሞ የዘለዓለምን ሕይወት ለመውረስ መሠረታዊ መስፈርት መሆኑን የሚያመለክት ነው:: ማቴ.19+19፡: በብሉይ ኪዳን ከነበረው አንፃር ባልንጀራ የሚለው ቃል በሐዲስ ኪዳን ሰፋ ያለ ሆኖ .እናገኘዋለን፡፡ ብዕለተ ዓ ርብ በመስቀል የፈሰሰው የክርስቶስ .ደም ለዓለም ሁሉ ማለትም ለደቂቀ አዳም ድኅነት በመሆኑና. ይህ ቤዛነ ትም ሕዝብንና አሕዛብን አንድ ያደረገ ስለሆነ ባልንጀራ የሚለው ቃል -ፍቺ በክርስቶስ;.አንድ አካል. የሆኑትን, ሁሉ የሚያጠቃልል ወደመሆን ሰፍቷል:፡: በዚህ ትርጉም መ ሠረትም ባልንጀራን መውደድ ማለት ሰውን ሁሉ መውደድ ሆኖ አናገኘዋለን፡፡
```

#### Rank 16: `10commandments:chunk-0108:unit-01`

- parent chunk ID: `10commandments:chunk-0108`
- similarity_score: 0.8576829433441162
- page_start: 44
- page_end: 44
- unit token count: 382
- extraction method: ocr
- quality score: 80.7
- ground-truth relevant parent: no

```text
ሕይወት 'እንዲ ኖሩ ማድረግ ባልንጀራን መውደድ ነው:: ወንበዴ ዲ ያብሎስ በተለያዩ ሁኔታዎች የሚያንገላታቸውን ' 'ደቂቀ አዳም ለመንፈሳዊ የሕይወት ትንሣኤ- ማብቃትና ነፍሳ ቸውን በኃጢአት ከመሞት መታደግም. ባልንጀራን መውደድ ነው::

በጥቅሉ ስንመለከተው በአርአያ ሥላሴ የተፈጠረ የሰውን ዘር ሁሉ ማንንም ከማን ሳያበላልጡ እኩል በሆነ - ፍቅር መመልከትና ማክበር ባልንጀራን መውደድ መሆኑን ማጤን ያስፈልጋል፡፡ ሐዋርያው ቅዱስ ያፅቆብም «ነገር ግን መጽሐፍ፡፦- ባልንጀራህን እንደራስህ ውደድ እንደሚል የንጉሥን የእግዚአብሔርን ሕግ ብትፈጽሙ መልካም ታደርጋላችሁ፤ ለሰው ፊት ግን ብታደሉ ኃጢአትን ትሠራ ላችሁ፥ ሕግም እንደተላላፊዎች ይወቅሳችኋል፡ነ:» በማለት የተናገረው ባልንጀራን መውደድ ማለት ሁሉን እኩል አድርጎ በአንድ የፍቅር ዓይን መመልከት' እንደሆነ ለማ ስረዳት ነው:፡ ያፅ.2፥8-9፡፡ ] ከዚህ በላይ የተመለከትናቸው. የመጽሐፍ. ክፍሎች ባልንጀራን መውደድ ማለት ሰውን ሀሌ. መው ደድ እን ደሆነ - አረጋግጠውልናል፡፡ አሥረኛው ; ትእዛዝ ' ደግሞ ባልንጀራን እንደራስ በመውደድ - መፈጸም . የሚገባው ትእዛዝ ነው:: «እንደራስ መውደድ» ሲባል ምን ማለት መሆኑን መመልከት አስፈላጊ ኝው:: ' እንደራስ! መውደድ ሰፊ ትርጉም ያለው 'ነው::' እንደሚከተለው እንመ 'ለከተዋለን፡፡ ‹. 17. ግ... |
```

#### Rank 17: `10commandments:chunk-0047:unit-01`

- parent chunk ID: `10commandments:chunk-0047`
- similarity_score: 0.8574864864349365
- page_start: 16
- page_end: 16
- unit token count: 180
- extraction method: ocr
- quality score: 82.86
- ground-truth relevant parent: no

```text
የሚለውን ትእዛዝ እንደመሻር ተወስዶ የሚያስቀጣ አይደ

ለም፡።- በሐዲስ ኪዳንም መድኃኒታችን ኢየሱስ ክርስቶስ «ለቀደሙት አትግደል እንደተባለ ሰምታችኋል የገደለም ሁሉ ፍርድ ይገባዋል» በማለት ሲናገር የጠቀሰው ሕግ በዘ ጸአት «አትግደል» የተባለውንና በዘሌዋውያን ደግሞ «ሰውን እስኪሞት ድረስ የሚመታ ፈጽሞ ይገደል» የሚ ለውን ነው: ዘጸ.29+13፡፡ ዘሌ.24+17፡፡፤ ከዚህም በላይ መግ ደል ብቻ ሳይሆን በወንድሙ ላይ የሚቆጣ ወንድ ሙንም የሚሰድብ የሸንጎ፤ የገሃነምም ፍርድ የሚገባው መሆኑን በመግለጥ ይህን ሕግ እንደአጠበቀው እንመለከታለን፡፡ ማቴ,.5፥21--23፡፡
```

#### Rank 18: `10commandments:chunk-0045:unit-02`

- parent chunk ID: `10commandments:chunk-0045`
- similarity_score: 0.8572631478309631
- page_start: 15
- page_end: 15
- unit token count: 262
- extraction method: ocr
- quality score: 80.66
- ground-truth relevant parent: no

```text
፡: በዝሙት ያገጸትን ሴት በጌታ ፊት በከሰሷት ጊዜ ጸሐፍት ፈሪሳውያን የጠቀሱት ይህን ሕግ ነበር፡ኔ፡ ዮሐ.8፥+5፡፡ ከዚህም ፣.- ሌሳ ማንም ይህን ትእዛዝ ተላልፎ ሰውን ቢገድል በተን ፡፣ ኮልም በባልንጀራው ላይ ቢሸምቅበትና ቢገድለው ፈጽሞ : - ይገል የሚል ትአዛዝ አለ፡፡ ዘ8.21፥12-14፡ በቅጥታ የገደለ ብቻ ሳይሆን በተዘዋዋሪ ለአንዱ ሰው መሞት ተጠ ያቂ የሚሆን መገደል እንደነበረበት በሕግ ተደንግጎ ነበር፤ «በሬው ግን አስቀድሞ ተዋጊ ቢሆን፥ ሰዎችም ለባለቤቱ ቢመ ሠክሩለት ባይጠብቀውም፥ ወንድንም ወይም ሴትን ቢገድል፥ በሬው ይወገር፣ ባለቤቱ ደግሞ ይገደል፡: ተብሎ ነበርና፡፡

ሸጸ.21+29፡፡

-. በብሉይ ኪዳን እንደተጻፈ የአግዚአብሔርን ስም በከንቱ የሚጠራ እንዲገደል ሕግ ይናገራል፤ ከትእዛዛት አንዱን ተሳልፏልና፡: ዘሌ.24፥16፡: የመጀመሪያውን ትእዛዝ
```

#### Rank 19: `10commandments:chunk-0110:unit-01`

- parent chunk ID: `10commandments:chunk-0110`
- similarity_score: 0.856878399848938
- page_start: 45
- page_end: 45
- unit token count: 406
- extraction method: ocr
- quality score: 85.0
- ground-truth relevant parent: no

```text
ነገር ግን እያ ንዳንዱ ባልንጀራው ከራሱ ይልቅ እንዲሻል በትኅትና ይቁጠር፤ እያንዳንዱ ለራሱ የሚጠቅመውን አይመልከት፥ ለባልንጀራው. ደግሞ ' እንጂ:> በማለት አጠናክሮታል፡፡ ፊልጵ;2፥2-4፡፡፡ በዚህም ባልንጀራን እንደራስ መውደድ

ማለት ፍቅርን በትሕትና , .መግለጥ መሆኑን እናስተውሳላለን፡፡

- ስለሆነም “ሰው -ባልንጀራውን እንደራሱ፣ ከራሱም አብልጦ የሚወደው ከሆነ የተቀደሰ የባልንጀራውን, ሰውነትና መንፈሳዊ ሕይወቱን ያጠፋ ዘንድ አይገድለውም፤. አካሉን በዝሙት አያረክሰውም፤ ሀብቱንም ሆነ ንብረቱን አይ ሰርቅበትም፣'፣በሐሰት አይመሰክርበትም፣ ንብረቱንና ቤቱን በመመኘትና. በመቅናት አይመቀኘውም፡፡ ከአሥርቱ ትእ ዛዛት መካከል የሰዎችን የእርስ በርስ ግንኙነት የሚመለ - ከቱችን ሁሉ የሚተላለፍ የፍቅርን ሕግ ይጥሳል፡ሱፁ: ባልንጀራ ውንም የማይወድ ሰው ትእዛዛትን እንዳይጥስ፣ ሕግም እንዳያፈርስ የሚከለክለው ገደብ የለም፡፡

ስለዚህ ለሰው ፍቅር የሌለው, ማንም ቢሆን ኅሊ ናውን የሚከብደውና በወንድሙ-. ላይም ክፉን እንዳያደርግ የሚቃወመው ውስጣዊ ሃሳብና ስሜት ስለሌለ ያእግዚአብሔ ርን ትእዛዛት በመተላለፍ ኃጢአትን እየፈጸመ የዲያብሎስ ባሪያ ሆኖ ይኖራል፡ኔ- ይህ እንዳይሆን ነው አምላካችን እግዚ አብሔር «ባልንጀራህን እንደራስህ ውደድ» በማለት ያዘዘጠ ው:፥ ነቢየ እግዚአብሔር ሳሙኤል «በውኑ የእግዚአብሔርን ቃል በመስማት ደስ እንደሚለው እግዚአብሔር በሚቃጠ
```

#### Rank 20: `10commandments:chunk-0109:unit-01`

- parent chunk ID: `10commandments:chunk-0109`
- similarity_score: 0.8568545579910278
- page_start: 44
- page_end: 45
- unit token count: 324
- extraction method: ocr
- quality score: 80.7
- ground-truth relevant parent: no

```text
በመውደድ - መፈጸም . የሚገባው ትእዛዝ ነው:: «እንደራስ መውደድ» ሲባል ምን ማለት መሆኑን መመልከት አስፈላጊ ኝው:: ' እንደራስ! መውደድ ሰፊ ትርጉም ያለው 'ነው::' እንደሚከተለው እንመ 'ለከተዋለን፡፡ ‹. 17. ግ... |

እንደሚታወቀው ሁሉ ማንም ቢሆን በራሱ ላይ ክፉን የሚመኝ፣ የሚያደርግም የለም፣ ሞትን የሚወድ የሚሻውም የለም፤ ማንም -መዋረድን፣ ርኩሰትን፣ ውድቀትንም የሚፈ ልግ የለም። ደግሞ ማንም 'ድኅነትን፣ ጸጋና በረከትን የማ ይሻ የለም፡ ማንኛውም ሰው ዓይነቱ የተለያየ ይሁን እንጂ ለራሱ መልካም የሆነውን ሁሉ ይሻል፡። መልካሙን ለማግኘት የተቻለውን ያህል የማይጥር፣ የለም:: እንዲህ ከሆነ ባልንጀራ ን እንደራስ መውደድ. ለራስ የሚሹትን መልካም ነገር ሁሉ ለባልንጀራ ማድረግ ማለት ነው፡:: በወንጌል ጌታችን ኢየሱስ ክርስቶስ «እንግዲህ ሰዎች ሊያደርጉሳችሁ የምትወዱትን ሁሉ - እናንተ ደግሞ እንዲሁ አድርጉላቸው፤ ሕግም ነቢ -ያትም ይህ ነውና:> በማለት ያስተማረው ይህንኑ የሚያ መለክት ነው፡:፡ ማቴ.7+12፡- በዚህ ትምህርት መሠረትም ሕግ በተባለች ኦሪት የታዘዘና በነቢያት ትንቢት የተሰበከው ፍቅር ይህ ነውና ባልንጀራን እንደራስ መውደድ ማለት ለራ ስ ቢያገኙት የሚወዱትን ለባልንጀራ ማድረግ ነው::
```

### C. Parent-ranking analysis

Parent rank follows the first time each parent appears in the top 20. The official metric keeps only the first five parents.

| Parent rank | Parent chunk | Best unit rank | Best unit score | Pages | Ground-truth relevant |
| --- | --- | --- | --- | --- | --- |
| 1 | `10commandments:chunk-0013` | 1 | 0.870754063129425 | 5–5 | no |
| 2 | `10commandments:chunk-0007` | 2 | 0.8683595657348633 | 3–3 | no |
| 3 | `10commandments:chunk-0086` | 3 | 0.8675439953804016 | 34–35 | no |
| 4 | `10commandments:chunk-0012` | 4 | 0.8668813705444336 | 5–5 | no |
| 5 | `10commandments:chunk-0087` | 5 | 0.8665153980255127 | 35–35 | no |
| 6 | `10commandments:chunk-0093` | 6 | 0.8658826947212219 | 38–38 | no |
| 7 | `10commandments:chunk-0088` | 7 | 0.8644039630889893 | 36–36 | no |
| 8 | `10commandments:chunk-0089` | 8 | 0.8643059730529785 | 36–36 | yes |
| 9 | `10commandments:chunk-0054` | 9 | 0.862360954284668 | 20–20 | no |
| 10 | `10commandments:chunk-0111` | 10 | 0.8621425032615662 | 46–46 | no |
| 11 | `10commandments:chunk-0081` | 11 | 0.8595633506774902 | 32–32 | no |
| 12 | `10commandments:chunk-0076` | 12 | 0.8583327531814575 | 30–30 | no |
| 13 | `10commandments:chunk-0085` | 13 | 0.8582947850227356 | 34–34 | yes |
| 14 | `10commandments:chunk-0107` | 15 | 0.8580265045166016 | 43–44 | no |
| 15 | `10commandments:chunk-0108` | 16 | 0.8576829433441162 | 44–44 | no |
| 16 | `10commandments:chunk-0047` | 17 | 0.8574864864349365 | 16–16 | no |
| 17 | `10commandments:chunk-0045` | 18 | 0.8572631478309631 | 15–15 | no |
| 18 | `10commandments:chunk-0110` | 19 | 0.856878399848938 | 45–45 | no |
| 19 | `10commandments:chunk-0109` | 20 | 0.8568545579910278 | 44–45 | no |

- chunk-0089 enters as unique parent 8 because its best unit, unit-02, is search rank 8 with similarity 0.864306. Seven other parents have a higher best unit. unit-01 of the same parent is only rank 14, so it does not improve the parent rank.
- chunk-0085 enters as unique parent 13. Its unit-01 is search rank 13 with similarity 0.858295. Its unit-02, which contains ከባልንጀሮቻችሁ, is outside the top 20, so it cannot move the parent earlier.

### D. False-positive analysis

Classifications cover units ranked above a relevant parent. Uncertain cases are marked.

- Rank 1, `10commandments:chunk-0013:unit-01`: **same terminology but different concept**. Page 5 discusses sacrificing truth for reputation and being a defender of falsehood. It uses ባልንጀራ, ሐሰት, and ትእዛዝ, which also occur in the question, but the passage is the first commandment's warning against worshipping reputation. It does not state the false-witness command.
- Rank 2, `10commandments:chunk-0007:unit-01`: **likely lexical similarity**. Uncertain. This is a general closing on page 3 about the commandments as a covenant and about studying each command. It does not mention false witness, lying, or a neighbor. The shared wording is ትእዛዝ. The score is almost tied with rank 1, so the reason it outranks the false-witness chapter is not fully clear from the text.
- Rank 3, `10commandments:chunk-0086:unit-02`: **genuinely semantically related**. This is the same eighth-commandment chapter on page 35. It teaches that the devil is the father of lies and that repeating an unverified report makes a person share in falsehood. It uses ሐሰት, ውሸት, and መመስከር. It does not contain the readable command «በሐሰት አትመስክር», which is why the benchmark does not treat this parent as the answer.
- Rank 4, `10commandments:chunk-0012:unit-01`: **same terminology but different concept**. Page 5, immediately before chunk-0013, is about worshipping reputation and hiding a neighbor's fault. የባልንጀራ and እውነት are prominent. The concept is idolatry of reputation, not the command against false witness.
- Rank 5, `10commandments:chunk-0087:unit-01`: **genuinely semantically related**. Still the false-witness chapter, page 35. It says a matter stands by two or three witnesses and that someone who repeats what they heard is not automatically a reliable witness. This is adjacent teaching about testimony, not the wording of the command.
- Rank 6, `10commandments:chunk-0093:unit-01`: **genuinely semantically related**. Page 38 continues the lying discussion: a half-truth is counted as falsehood, and false prophets are condemned. Same chapter and same sin, later than the command statement.
- Rank 7, `10commandments:chunk-0088:unit-01`: **genuinely semantically related**. Page 36 gives examples of false witness against Christ, Stephen, and Naboth. በሐሰት መመስከር is explicit. Its score is 0.86440, and the relevant command unit immediately below it is 0.86431. This is the nearest same-chapter neighbor.
- Rank 9, `10commandments:chunk-0054:unit-01`: **other**. Uncertain. Page 20 is the fifth commandment, about killing an unborn child. It shares the pattern of naming a commandment, not the false-witness topic. Why it sits between the two relevant parents is unclear.
- Rank 10, `10commandments:chunk-0111:unit-01`: **same terminology but different concept**. Page 46 summarizes all the commandments as love of God and neighbor. It quotes በውሸት አትመስክር inside that list. The command wording is present, but the passage is not the exposition of false witness.
- Rank 11, `10commandments:chunk-0081:unit-01`: **other**. Uncertain. Page 32 explains theft, including theft that begins in desire. It is not about false witness. A lexical reason is not obvious.
- Rank 12, `10commandments:chunk-0076:unit-01`: **same terminology but different concept**. Page 30 is the seventh commandment, አትስረቅ. It says theft is later joined to በሐሰት አትናገር. That phrase is close to the false-witness command, while the passage itself teaches about stealing.

### E. Relevant-passage analysis

1. Does the Amharic passage clearly answer the question? Yes. chunk-0085 says the eighth commandment's false witness is lying. chunk-0089 states «በሐሰት አትመስክር» and says the command binds both the speaker and the listener. The Exodus quotation line in chunk-0085 is OCR-corrupted, as the approved ground truth already records.
2. Does the question wording differ from the passage? The question asks what the command about false witness against a neighbor says. The clearest command sentence does not contain ባልንጀራ. That word appears in chunk-0085 unit-02 and in the page-5 reputation passages that rank above the command.
3. Does the passage use indirect theological language? The chapter explains lying, the devil, and historical false witnesses before and around the short command sentence. The command itself is direct once it appears.
4. Is the relevant unit short, long, or structurally unusual? chunk-0089 unit-02 is short, 150 tokens, and is cut off at 'የቤተ-'. chunk-0085 unit-01 is a normal-length unit whose first quotation line is unreadable OCR.
5. Is the relevant unit coherent? unit-02 of chunk-0089 is a coherent statement of the command. unit-01 of chunk-0085 is a coherent opening, but the neighbor phrase the question uses is in the next unit.
6. What could make embedding retrieval difficult? The readable command is a short tail after a long example. The official Exodus wording is not readable. Many nearby units repeat ሐሰት, ውሸት, and ምስክር, so the distinctive sentence has little unique signal.

### F. Most likely failure

**C. Strong semantic distractors in the corpus.** Confidence: medium.

Five of the seven units above the first relevant unit are either the same false-witness chapter or passages that share ባልንጀራ and ሐሰት. The nearest neighbor, chunk-0088, is only 0.000098 similarity above the command unit. The whole top 20 sits inside a 0.014 similarity band. Query wording and the split that leaves ባልንጀራ outside the top 20 contribute, but the dominant pattern is a crowd of near-duplicate false-witness passages.

A single category does not exhaust the miss. B and D are visible contributors. A is possible because the margin is so small, but the higher units are interpretable rather than random.

### G. Comparison with the original chunks

`chunk-0085`: The parent is one OCR chunk on page 34. It was split into unit-01 (293 tokens: heading, corrupted Exodus line, and the definition that false witness is lying) and unit-02 (323 tokens: speak truth with your neighbor, and the habit of lying). Only unit-01 is in the top 20. The question's ባልንጀራ wording is in unit-02, which this search did not return. That split can plausibly weaken this question. It does not fully explain the miss: the heading unit itself still ranks 13th, below several same-chapter units.

`chunk-0089`: The parent is one OCR chunk on page 36. unit-01 (372 tokens) is examples of false accusation and ranks 14. unit-02 (150 tokens) is the command and ranks 8. The split placed the clearest answer in the higher of the two units. The parent is still eighth because seven other parents score higher. The split did not hide the command sentence.

Units of `10commandments:chunk-0085` after refinement:

`10commandments:chunk-0085:unit-01` — 293 tokens, pages 34–34

```text
ስምንተኛው ትእዛዝ

«/,ል 2ድራያ ሏሪ በፊፀት ለ4ፉመኃዕአዕር› ዘጸ.20+16፡፡

በሐሰት መመስከር መዋሸት ነው:: በቅዱስ መጽሐ ፍም ስለሐሰት የተነገሩት ቃላት የመዋሸትን አስከፊ ገጽታ የሟያሳዩ ናቸው፡: ስለዚህም ነገር ጠቢቡ ሰሎሞን «ውሸተኛ ከንፈር በእግዚአብሔር ዘንድ አስጸያፊ ነው» በማለት ተና - | ግሯል: ምሳ.12፥22፡:: መዋሸት በአግዚአብሔር ዘንድ የተጠ - ፤!

ላ በመሆኑም ቀደም ብሎ በዘሌዋውያን «እናንተም እርስ ' በርሳችሁ ሐሰት አትነጋገሩ»የሚል ትእዛዝ ተሰጥቶ ነበር: ዘሌ.19፥11፡፡: ይህም በሰዎች ዘንድ ሐሰት መናገር ያለተፈ ቀደ መሆኑን የሚያስገነዝብ ነው:: ከዚህ በመነሣት ሐሰት ወይም ውሸት ምንድነው? ለሚለው ጥያቄ መልስ መስጠቱ አስፈላጊ ነው፡፡ ሐሰት /ውሸት/ የሆነውን አልሆነም፤ ያለሆነ ውን ሆነ ብሎ 'ለሌላው; ሰው መናገር 'ወይም አሉታዊውን አዎንታዊ አዎንታዊውን' ደግሞ አሉታዊ አድርጎ በማቅረብ የተሳሳተ መረጃ መስጠት ማለት ነው:: ሐሰት የእውነት ተቃራኒ ነው::
```

`10commandments:chunk-0085:unit-02` — 323 tokens, pages 34–34

```text
በዚህ ላይ በመመሥረት ነው መምህረ አሕዛብ የተ ባለው ሐዋርያው ቅዱስ ጳውሎስ ለኤፌሶን ምእመናን በሳ ከው መልእክቱ «ስለዚህ ውሸትን አስወግዳችሁ፥+፥...እያን " ዳንዳችሁ ከባልንጀሮቻችሁ ጋር እውነትን ተነጋገሩ: በማ ለት የመከረው፡: ኤፌ.4፥25፡፡ በዚህ ምንባብም ቢሆን እው ነትን መናገር የክርስትና መሠረት .መሆኑ በግልጥ ነው የተመለከተው፡ ብሌያትም ሆኑ ሐዲሳት ተባብረው ' ሐሰ ትን አውግዘውታል፤ ክፉ ነውና: መዋሸት በሰውም በእግዚአብሔርም ዘንድ መጠላቱ ኃጢአት ስለሆነ ነው፡፡ ውሸት ከፍርሃትና ከደካማ ባሕርይ የሚመነጭ ሊሆን ይችላል፡፡ በራሱ 'የሚተማመንና እውነ ተኛ ሰው አይዋሽም፣ የተሰጠውንም ኃላፊነት በሚገባ ይወ ጣል፡። በራሱ የማይተማመን ደካማና ስነፍ ሰው መዋሸትን የስንፍናው መሸፈኛና ቀላል የመፍትሔ አማራጭ አድርጎና .:0 ..: . ይጠቀምበታል፡፡ አልፎ አልፎም ውሸትን ለቀደመ ሐሰት መሸፈኛ ሲጠቀሙበት የሚታዩም አሉ፡ እንዲህ ዓይነቶቹ ሰዎች ከአንዱ ውሸት ወደሌላው እየቀጠሉ ሲዋሹ ይኖራ ሉ፣ መዋሸታቸውን ለመሸፈን መዋሸትን ለምደዋልና፡፡
```

Units of `10commandments:chunk-0089` after refinement:

`10commandments:chunk-0089:unit-01` — 372 tokens, pages 36–36

```text
ኪዳን ንግሥቲቱ ኤልዛቤል በኢይዝራኤላዊው በናቡቴ 'ላይ ያቆመቻቸው የሐ ሰት ምስክሮች «ናቡቴ እግዚአብሔርንና ንጉሥን ሰድቦአል ብለው" በናቡቴ ላይ መሰከሩ:: የዚያን ጊዜም ከከተማ አውጥተው እሰኪሞት ድረስ ወገሩች›፡፡ 1ነገ,20፥13፡፡

.።+ ሐዋርያው ቅዱስ ጳውሎስም «በክብርና. በውርደት፥ በክፉ -ዉወሬና በመልካም.-ወሬ ራሳችንን እናማጥናለን፤ አሳቾች ስንባል እውነተኞች ነን»: በማለች የተናገረው በሐዋርያዊ አገልግሎታቸው -ላይ በሐሰት ይናፈስ የነበረውን አሉባልታ የሚመለከት ነበር፡ 2ቆሮ.6+8:: ከዚህም በላይ በቅዱሳን ላይ ስለተነገረው የሐሰት ምስክርነት ሁሉ እንጻፍ ቢባል ጊዜም አይበቃም፡፡ ብዙ ቅዱሳን በሐሰት ምስክርነት የተነሣ ያለ በደላቸው መከራን ተቀብለዋል፤ የነፍስ መሥዋዕትነትም ጭምር ከፍለዋል፡ፎ፡ ለምሳሌ ያህል ቅዱስ አትናቴዎስ ሐዋር ያዊ በዝሙትና በነፍስ ግድያ፤-ሶርያዊው ቅዱስ አብርሃም፤ ታላቁ መቃርዮስ፣ አባ መሪና በዝሙት የተከሰሱት በሐሰት እንደነበር ቅዱሳት ድርሳናት ያስረዳሉ፡፡ እነዚህ ቅዱሳን - አበው በሐሰት ከተከሰሱበት ኃጢአት ነፃ መሆናቸው ተረ ጋግጧል፡፡ -ስለዚህ--እንግዲህ-- በሐሰት ለሟነገር- ክስም ሆነ...

ወሬ ጆሮን ከመስጠት መቆጠብ ለሰው ሁሉ ጠቃሚ ነው::
```

`10commandments:chunk-0089:unit-02` — 150 tokens, pages 36–36

```text
«በሐሰት አትመስክር» የሚለው ትእዛዝ ዋሽቶ የሚናገረውንና ሐሰተኛ ወሬን የሚሰማውንም ሰው ሁሉ የሚመለከት ነው:: ሐሰት ወሬን የሚሰማና የሚቀበል ሰው ውሽተኛውን የበለጠ እንዲዋሽ ይገፋፋዋልና በኃጢአት ላይ ኃጢአት እንዲሠራ ምክንያት ይሆነዋል፡፡ በዚህ መሠረትም በሐሰት ኃጢአት ተናጋሪውና አድማጩ ሁለቱም ተሳ ታፊዎች ናቸው፡፡ በቅዱስ መጽሐፍ የምናገኘው የመጽሐፍ ቃል የሚያስተምረው ሐሰተኛ ወሬን መስማትና | ማስተ 2ባትም ተገቢ አለመሆኑን ነው: "ምሳ.29፥12፡፡ 'የቤተ-
```

## paraphrased-05

### A. Question information

1. question_id: `paraphrased-05`
2. exact question: የተመኙትን ነገር ማግኘት ምኞትን ከማጥፋት ይልቅ የሚጨምረው እንዴት ነው?
3. question_type: paraphrased
4. finalized expected concept: Fulfilling a desire does not free a person from desiring; it increases desire. The person who gained the money he wanted wants still more and does not say that what he gathered is enough. Any satisfaction is only temporary and does not stop further desire.
5. source document: 10commandments.pdf
6. source pages: 10commandments:chunk-0102 pages [41]
7. relevant parent chunk IDs: `10commandments:chunk-0102`
8. Qualifications preserved by the approved ground truth:
   - Desire increases when it is fulfilled.
   - Satisfaction is described as temporary. The passage does not say that satisfaction never occurs.

Exact Amharic text of each relevant parent chunk:

`10commandments:chunk-0102` pages 41–41

```text
ምኞትን መፈጸም ሰውን ከመመኘት አያድነውም የበለጠ የምኞትን ፆር ይጨምርበታል አእንጂ፡: በዓለማችን እንደምናየው ገንዘብ ለማግኘት ተመኝቶ ገንዝብን ያገኘሰው ተጨማሪ ገንዘብ ለመሰብሰብ ይመኛል እንጂ የሰበሰብኩት ይበቃኛል አይልም፡፡

አባታችን አዳም በገነት ያሉትን ዛፎች ሁሉ ከአንዲቱ በቀር አንዲያዝዝባቸው ሥልጣን ተሰጥቶት ነበር፡። በዚህ ባለመርካቱም ያቺን አንዲቱን ደግሞ ተመኛት ከፍሬዋ ለመብላትም ጓ5:፡ሪ፥ ሁሉ ያለው ንጉሠ አክዓብ የኢይዝራኤላዊውን የናቡቴን ትንሽ መሬት ተመኘ፡: ሰባት ሚስቶች የነበረው ዳዊት የወታደሩን /የባለሟሉን/ የኦርዮን ሚስት ተመኘ፡፡ ንጉሥ ሰሎሞንም ምኞቱን ለማርካት አስከ መጨረሻው ተዓዝ "ዓይኖቼንም ከፈለጉት ሁሉ አልከለክልኳቸውም በማለት መጨረሻ የሌለው ምኞቱን ገልጣል፡፡ መክ 2፡10: በዚህ ወጤትም በመቶዎች የሚቆሩ ሚስቶች ለእርሱ አደረገ በማይሞተው ቃሉም "ዓይን ከማየት አይጠግብም ጆሮም ከመስማት አይሞላም፡፥ ፈሳሾች ሁሉ ወደ ባሕር ይሄዳሉ፡፡ ባሕሩ ግን አይሞላም" በማለት ሊረካ የማይችል የምኞቱን ነገር ተናግሯል፡፡ መክ፲፡7ሀ8፡፣ በዚህም ምኞት ፈጽሞ እርካታ ማግኘት ጊዜያዊ ብቻ እንጂ ዳግመኛ ከመመኘት የሚገላግል መፍትሔ አለመሆኑን አስተምሮናል ለዚህ መፍትሔ የሚመኝ ሥጋን ራስን በመግዛት ልጓም መቆጣጠር ነው የሚሻለው ግን ፈጽሞ ከምኞት መሸሽ ነው፡፡ ያገባው ብዙም ሚስቶች የነበሩት ዳዊት እርካታን በፈለገና ራሱን መግዛት ባልተቻለው መጠን በምኞት ድል እንደተመታ ያላገባው ዮሴፍ በንጽሕና ሆኖ ራሱን በመግዛቱና ምኞትን ያሸነፋት የሸሹት ሰው እንጂ የተጋፈጡት አይደሉምና በጥበብ ሆኖ ከክፋ የሥጋ ምኞት መሸሽ መድኃኒት መሆኑን አውቀን ገንዘብ ልናደርገው ይገባናል፡፡ ] የምኞት ዓይነቶች፡- ሐዋርያው ቅዱስ ጳውሎስም "ሥጋ በመንፈስ ላይ ይመኛል" በማለት ምኞት ከሥጋ ፈቃድ የሚመነጭ መሆኑን ተናግሯል፡፣ ገላ 5፡17፡፡ . ስለዚህ ምኞትን የሚያስከትል የሥጋ ፈቃድ ተዘርዝሮ የሚያበቃ አይደለም፡፡
```

### B. Top-20 retrieval analysis

These are the 20 units returned before parent collapse, in the official ranking.

#### Rank 1: `10commandments:chunk-0101:unit-01`

- parent chunk ID: `10commandments:chunk-0101`
- similarity_score: 0.8721902966499329
- page_start: 41
- page_end: 41
- unit token count: 267
- extraction method: ocr
- quality score: 85.33
- ground-truth relevant parent: no

```text
መ. የስይጣን ፆር:- ሰይጣን በአባብ ሥጋ ተሰውሮ በሔዋን ኀሲና ውስጥ ምኞትን አንደመረጸ ሁሉ ዛሬም በሰው የስሜት ሕዋሳት ተጠቅሞ የምኞት ጸጾር ሊቀሰቅስ ይችላል፡፡

ፉፉ ምኞት " የሚገ ዴ የሰው ልጅ ምኞት በደከመውና ተገዥ ባደረገው ጊዜ ዳግመኛ እየጓጓሁ ከመቸገር ይህን ምኞትን ፈጽሜው ባርፍ ይሻለኛል በማለት ራሱን ያታልል ይሆናል፡፡ ምኞት ግን በአንድ ጊዜ አርካታ ከልቡና የሚነቀል ከንሊናም የሚጠፋ አይደለም: የተጠማ ሁሉ አንድ ጊዜ ጠጥቶ ዳግመኛ እንደሚጠማ ምኞቱም በመፈጸም ደስታን የሚያገኝ የሚመስለውና ፈጽሞ እንደ ሚረካ በማሰብ የተመኘውን የፈጸመ ሰው እንደገና ደግሞ ይመኛል ምኞቱም ማብቂያ የለውም፡ ምኞትን መፈጸም ሰውን ከመመኘት አያድነውም የበለጠ የምኞትን ፆር ይጨምርበታል አእንጂ፡: በዓለማችን እንደምናየው ገንዘብ ለማግኘት ተመኝቶ ገንዝብን ያገኘሰው ተጨማሪ ገንዘብ ለመሰብሰብ ይመኛል እንጂ የሰበሰብኩት ይበቃኛል አይልም፡፡
```

#### Rank 2: `10commandments:chunk-0099:unit-01`

- parent chunk ID: `10commandments:chunk-0099`
- similarity_score: 0.8673075437545776
- page_start: 40
- page_end: 41
- unit token count: 429
- extraction method: ocr
- quality score: 85.33
- ground-truth relevant parent: no

```text
ነው፡። ሐዋርያው ቅዱስ ጳውሎስም ለጢሞቴዎስ 'ከክፋ የጎልማሳነት ምኞት ግን ሽሽ" ሲል የመከረው ሰዚህ ነወ፡፡ 2ኛ ጢሞ 2:22 ምኞት ከተመኙት እስኪፈጸም ድረስ ያለማቋረጥ የሚዋጋ ፆር በመሆኑ መሸሽ አማራጭ የሴለው መፍትሔ ነው፡፡

ምኞት በሰው ልቡና ውስጥ ሥፍራ በተሰጠው መጠን የሰውን ፈቃደኝነት ያገኛል ስለእርሱ በታሰበ መጠንም በልቡና ውስጥ ያድጋል ከቪያም ስለ አርሱ በማሰብ ወደ መደሰት ለመፈጸም ወደ ማስጐምጀት ቀጥሎም በተግባር ወደ መፈጸም ያደርሳል፡፡ - ስለዚህ በመመኘትና የተመኙትን ፈጽሞ ከመውደቅ መጀመሪያውኑ ከመመኘት መሸሽ እጅግ ጠቃሚ ነው:፡፥: የሰው ባሕርይ ደካማ ነውና ከሥጋው የተነሣ ስለሚመኘው ኃጢአት ከማሰብ ጀምሮ በእርሱ ወደ መመራት ወደ መፈጸም ወደ መደጋገም በአርሱም ወደ መለከፍ ከዚያም አልፎ ለሚመኘው ነገር ወደ መገዛት ይደርሳልና ጠንቀኛ ከሆነው ምኞት አብዝቶ ራስን መቆጠብ አስፈላጊ ነዐ፡፡

ምኞት የሚያሰከትለው አደጋ አብዝቶ ራስን መቆጠብ አስላፈጊ ነው:፡ራ፡ ምኞት የሚያሰከትለው አደጋ ከዚህ በላይ በተጠቀሰው ብቻ የሚያበቃ አይደለም፡፥ ሰወ ምኞቱን ለመፈጸም ሲል በሌሳ ኃጢአት ሲወድቅም ይችላል፡- ለምኞቱ መፈጸም ብሎ ሊዋሽ

ሊያታልል ሊሰርቅ ሊገድልና ሌላ ኃጢአትም ሊሠራ ይችላል፡። ከዚህ ሁሉ ምኞትን ከሥሩ ነቅሎ ከልቡና ማውጣት ተገቢ ነው፡። ስለዚህ መነሻውም መድረሻውም አደገኛ ከሆነ ከዚህ የመመኘት ኃጢአት መሸሽና ማምለጥ አስፈላጊ ነው፡፡

ችት የሚደርጉ ምክገ፻ጀችች
```

#### Rank 3: `10commandments:chunk-0098:unit-02`

- parent chunk ID: `10commandments:chunk-0098`
- similarity_score: 0.867198646068573
- page_start: 40
- page_end: 40
- unit token count: 163
- extraction method: ocr
- quality score: 85.58
- ground-truth relevant parent: no

```text
----.--- . - - . -.- ሰው ከምኞት ጋር በተፋጠጠ ጊዜ ከምኞት ከመታገል ይልቅ የሚበጀው ከመመኘት መሸሽ ነው፡: ምክንያቱም ምኞትን ከማሸነፋ አስቀድሞ ሊሽነፍና ልቡናውም በምኞት ጦር ተወግቶ በምኞት መርዝ የተነደፈ ሊሆን ይችላልና ነው፡። ሐዋርያው ቅዱስ ጳውሎስም ለጢሞቴዎስ 'ከክፋ የጎልማሳነት ምኞት ግን ሽሽ" ሲል የመከረው ሰዚህ ነወ፡፡ 2ኛ ጢሞ 2:22 ምኞት ከተመኙት እስኪፈጸም ድረስ ያለማቋረጥ የሚዋጋ ፆር በመሆኑ መሸሽ አማራጭ የሴለው መፍትሔ ነው፡፡
```

#### Rank 4: `10commandments:chunk-0094:unit-02`

- parent chunk ID: `10commandments:chunk-0094`
- similarity_score: 0.8652994632720947
- page_start: 39
- page_end: 39
- unit token count: 227
- extraction method: ocr
- quality score: 81.36
- ground-truth relevant parent: no

```text
ሺነ” 5 አንዳንድ ሰዎች ከመበሳጨት ወይም ከመፍራት ወይም ስለአንድ ነገር የሚጠይቃቸው ሰው ከሚያ ሳድርባቸው ጫና የተነሣ ሊዋሹ ይችላሉ፡- ከመዋሸት ይልቅ ግን በእንደዚህ ያለ ጊዜ ዝምታ. መልካም መሆኑን ማወቅ ተገቢ ነው:: በሐሰት ራስን ለማዳን ከመሞከር ምንም ይሁን ምን የንግግርን አቅጣጫ በመቀየርም' ቢሆን፣ መልስ ላለመስጠት ይቅርታ 'በመጠየቅም ቢሆን፣ በተቻለ መጠን በማስተዋልና እውነትን በመናገር ራስን መከላከልና ስለተሠራው ስሕተት ይቅርታ መጠየቅ መልካም ነው:፡: አንዳንድ ሰዎች ሳያውቁ እንደዐወቁ፣ ሳይሆኑም እንደሆኑ በማስመሰል የሚኩራሩ. በመሆኑና አለማወ ቃቸውንም እንዳይታወቅባቸው ስለሚዋሹ መዋሸትን እንደመሸፈኛ ሊጠቀሙበት ይችላሉ: አንዱን ኃጢአት ለመሸፈን በመዋሸት ተጨማሪ ኃጢአት ከመሥራት - . አላውቅም በማለት እውነት መናገሩ የተመረጠና, ተገቢም ... .

ነው:: .
```

#### Rank 5: `10commandments:chunk-0096:unit-01`

- parent chunk ID: `10commandments:chunk-0096`
- similarity_score: 0.8636518120765686
- page_start: 40
- page_end: 40
- unit token count: 446
- extraction method: ocr
- quality score: 85.58
- ground-truth relevant parent: no

```text
ዘጠነኛው ትእዛዝ

አትመኝ "የባልንጀራህን ቤት አትመኝ የባልንጀራህን ሚስት ሎሌውንም ገረዱንም በሬውንም አህያውንም ከባልንጀራህ ገንዘብ ሁሉ ማንኛ ውንም አትመኝ' ዘጸ 20፡:፲7 ምኞት ምንድን ነው?

ምኞት የስው ልጆች በዓይናቸው ያዩትን በእጃቸው የዳሰሱትን በጆሮአቸው የሰሙትን ልባቸው የወደደውንና የፈቀደውን ለማግኘት በኅሊናቸው ሰሌዳ ላይ የሚቀረጽ መሻት /ፍላጎት/ ነው፡ጉ-፡-- ይህ ፍላጎት መንፈሳዊ ሥጋዊና ሰይጣናዊ ተብሎ ይከፈላል፡፡

መንፈሳዊ፡:- ቀደምት ቅዱሳት አበው የተጋደሉትን መንፈሳዊ ተጋድሎ ከገድላቸው ተረድቶ የእነርሱን አሠረ ፍኖት ለመከተልና እነርሱ ያገኙትን ጸጋ ለማግኘት /እንደአእርሱ ለመፃን/ በልብ ጽላት ላይ ተቀርጾ መከራውን ፈተናውን ሁሉ በትፅግሥት እንዲቀበሉ የሚገፋፋ ኃይሉ መንፈሳዊ ምኞት ይባላል፡ የእግዚአብሔርን መንግሥት ካልተመኙ ለመንፈሳዊ ተጋድሎ መብቃት አይቻልምና፡፡

ሥጋዊ የዓይን አምሮት የሥጋ ፍላጎትን ተከትሎ የሚመጣ ሲሆን ጉዳትም ጥቅምም አለው ለምሳሌ ሌሎች የደረሱበት ጥሩ ደረጃ ላይ ለመድረስ ዶክተር የሆኑትን አይቶ ዶክተር ለመሆኑ አስቀድሞ ወስጣዊ መሻት በልቦና መቀረጽ አለበት:: ይህም ተማሪውን ተግቶ አንዲጠና ሠራተኛውን ጠንክሮ እንዲሠራ ይገፋፋዋል፡- ስለዚህ ለሥጋዊ ሕይወቱ ይህ ዓይነት ምኞት ያስፈልገዋልና በክርስትና ትምህርት አይወገዝም፡፡

በአንጻሩ ግን ሌላው የደከመበትንና ሳቡን ያንጠፈጠፈበትን ሀብት እጅና አግርን አጣምሮ የአኔ ባደረገው እያሉ መመኘት ሲብስም ያልደከሙበትን ሀብት ለራስ ለማድረግ ሰይጣናዊ መንገድ መጠቀም ከእግዚአብሔር አንድነት የሚለይ ነው፡፡
```

#### Rank 6: `10commandments:chunk-0081:unit-01`

- parent chunk ID: `10commandments:chunk-0081`
- similarity_score: 0.8620849251747131
- page_start: 32
- page_end: 32
- unit token count: 396
- extraction method: ocr
- quality score: 83.52
- ground-truth relevant parent: no

```text
ከሥራ መቅረት ወዘተ ከመለመዱ የተነማ ብዙዎች ኃጢአት ሳይመስላቸው የሚፈጽሙት ነው፡ፎ፡ እንዲሁም አንድ የመሥሪያ ቤቱ የፅቃ ግዚ ክፍል ሠራተኛ የሆነ ሰው አሮጌ ቢገዛ ወይም ያልተገዛበትን ዋጋ በደረሰኝ ቢያሠራ የሰረቀ አይመስለውም፡፡

ወደ ነጋዴውም ኀብረተሰብ ስንገባ የባሰ አንጂ የተሻለ ነገር አናገኝም፡፡ በሜትርና በሚዛን ከማጭበርበር አልፈው ብዙ ሲስሩ እናገኛቸዋለን፡፡ እህል ነጋዴው አፈርና ገለባ ይደባልቅበታል ኪሎ እነዲያነሣም ውኃ ያርከፈክፍበታል፡፡ በርበሬ ነጋዴው ሸክላ ቅቤ ነጋዴው ደግሞ ሙዝ ድንች ይቀላቅላል።፡- አሮጌውን እንደ አዲስ የሚሸጠውን አጅ መንሻ መስጠት ሕጋዊ ያልሆነውን ንግድ የሚያካሂደውን ቤት ይቁጠረው፡: ይህ ሁሉ የራስ ያልሆነው አለአግባብ መውሰድ ነውና ስርቆት ነው፡፡

ለመሆኑ ሰዎች ለምን ይሰርቃሉ? አንድ ሰው ወደ ስርቆት ኃጢአት የሚገፋፉት ነገሮች/ ምንጮች/ ምንድን ናቸውን 1. ምኞት:- ያልተሰጠንና የራስ ያልሆነውን ነገር ወይም ያዩትን ሁሉ ለሪስ እንዲሆን መመኘት ወደ ስርቆት ያመራል፡፡

አንድ ገንዘብ የሌለው ሰው ገንዘብ ሳይኖረው ብዙ ነገሮች እንዲያሟሉለት ቁጭ ብሎ ማይሰራ የሚመኝ ከሆነ የግድ ያንን የፈለገውን ነገር ለማሟላት ወደ ሰርቆት ሊያመራ ይችላል፡፡ ፊልጵ «11 2. ችግር :- አንዳንድ ሰዎች ሳይወዱ በችግር ምክንያት ሲሰርቁ ይችላሉ፡ ለምን እንደሠረቁም ሲጠየቁ ቸግሮኝ ነው ይላሉ፡። ይሁን አንጂ ቢቸግርም ጠይቆ /ለምኖ/ መውሰድ /ማግኘት/ ሲቻል መስረቅ አይገባም፡:
```

#### Rank 7: `10commandments:chunk-0059:unit-01`

- parent chunk ID: `10commandments:chunk-0059`
- similarity_score: 0.8604065179824829
- page_start: 22
- page_end: 23
- unit token count: 379
- extraction method: ocr
- quality score: 81.28
- ground-truth relevant parent: no

```text
በዚህ. መልክ ነፍሳትን እያጠመዱ ከእግዚአብሔር ሕግ በመለየት የኃጢአት ባሪያ ለማድረግ ቀንና ሌሊት የሚደክሙ ዓለማውያን በየዕለቱ ስንት ነፍሳትን እየገደሉ ይውሉ ይሆን? የዚህ ወንጀልና ኃጢአት ተሳታፊና ተባባሪ ከመሆን ይሰውረኝን፡፡

ከዚህም ሌላ የተሳሳተ ትምህርተ ሃይማኖች በማስተ ማር የሰው መንፈሳዊ ሕይወት በኑፋቄ የሚመርዙና በተዛባ መንገድ የሚመሩ ሰዎችም ነፍሰ ገዳዮች ናቸው: በቀጥተኛ ሃይማኖት ጸንቶ ምግባር ትሩፋት ሠርቶ የዘለዓለምን ሕይ ..-ወት - እንዳይወርስ - እንቅፋት - ሆነዋልና::- ይህም--በሥጋ-.-.---..--.---.............

ከመግደል የከፋ. ነው:: በሥጋው የሞተ በነፍሱ የመዳን ዕድል ሊኖረው ይችላል፤ በነፍሱ የሞተ ግን የሚጠብቀው የዘለዓለም መከራ ነው:: በዚህ አንፃር በብዙ ሺዎች የሚቆጠሩችን ምእመናን.. ከእውነተኛው የሃይማኖት መንገድ በማስወጣት ለመናፍቅነት የዳረጉአቸው እነአርዮስ፣ መቅዶንዬስ፤ ንስጥ ሮስ፣ , ሉተር፤- የይሆዋ ምስክሮች መሥራች. ቻርልስ ራስል ወዘተ እና የእነዚህ ሁሉ ኑፋቄ የወለዳቸው መናፍቃንና ሌሎችም ሁሉ በነፍሰ ገዳይነት ከሚጠየቁት መካከል ዋና ብሽ ናቸው፤ ' 'የግድያውን መንገድ 'የከፈቱት እነርሱ “ው:

ስለዚህ ነገረ ሃይማኖትን የሚያስተምር ሁሉ ቀደምት አበው: ካስተማሩት የተለየ. እንዳይናገር መጠንቀቅ ይገባዋል፡፡
```

#### Rank 8: `10commandments:chunk-0104:unit-02`

- parent chunk ID: `10commandments:chunk-0104`
- similarity_score: 0.8601696491241455
- page_start: 42
- page_end: 42
- unit token count: 383
- extraction method: ocr
- quality score: 78.42
- ground-truth relevant parent: no

```text
እንዲሸጥ ያደረገው የመብል ምኞት ነወ፡- ከፍ 25:29-3ፋኑራ: የእሥራኤላውያንም መጎምጀትና" የምንበላውን ሥጋ ማን ይሰጠናል በግብጽ ያለዋጋ እንበላው የነበረውን ዓሣ ዱባውንም በጢኹንም ኩራቱንም ሽንኩርቱንም እናስባለን '' በማለት ማልቀስ ከዚህ የመመገብ ምኞት ጋር ተመሳሳይነት አለው፡፡ ዘጉት1፲፡45፡፤ እሥራኤል የተመኙትን ሥጋ አግዚአብሔር ሰጣቸው ነገርግን በከባድ መቅሰፍት ደግሞ መታቸው ይህም ለክፋ ምኞታቸው መቀጣጫ ነው:፡: ያም ሥፍራ የምኞት መቃብር ተብሎ ተጠራ የጎመጁ ሕዝብ በዚያ ተቀብረዋልና ዘጉት 1፲፤፲:3ፋ፡ ገንዘብ ምኞትም ንብረትን ለማደራጀት መመኘትም አለ:፡፥: ስለዚህም እግዚአብሔር የባልንጀራህን ቤት አትመኝ በማስት አዝዞአል የክብርና የታዋቂነት የሥልጣንና የማዕረግ የታላቅነት የውበትና የጌጠኛነት ወዘተ ምኞቶችም አሉ፡፡ እነዚህ ሁሉ ወደውድቀት የሚያደርሱ የጥፋት መንገዶች ናቸው፡፡ ዲያብሎስም የወደቀው ወደ ሰማይ ዐርጋለሁ ዙፋኔንም ክእግዚአብሔር ከዋክብት በላይ ከፍ ከፍ አደርጋለሁ ከደመናዎች ከፍታ በላየ አርጋለሁ በልዑልም እመሰላለሁ በማለት የማይገባውን ለማግኘትና ለመሆን ካደረበት ምኞት የተነሣ ነው፡፥ ኢሳ14፡13-.1ፋ፣ኑ እንዲሁም ዲያብሎስ እንደ እግዚአብሔር ትሆናላችሁ ባላቸውጊዜ አዳምና ሔዋን ለመውደቅ የበቁት ባደረባቸው ከፍተኛ ምኞት የተነሣ ነበር፡፡
```

#### Rank 9: `10commandments:chunk-0084:unit-01`

- parent chunk ID: `10commandments:chunk-0084`
- similarity_score: 0.8600041270256042
- page_start: 33
- page_end: 33
- unit token count: 358
- extraction method: ocr
- quality score: 78.38
- ground-truth relevant parent: no

```text
1፡13-21 ያን ጊዜ ነው አሥራት ማውጣትና የራስ ያልሆነውንም አለመፈለግ የሚቻለው፡፡ ሐዋርያው ቅዱስ ጳውሎስም

"ዙሮዬ ይበቃኛል" የሚለው ግን አግዚአብሔርን መምሰል እጅግ ማትረፊያ ነው ወደ ዓለም ምንም እንኳ አሳመጣንምና አንዳችም ልንወስድ አይቻለንም ምግብና ልብስ ከኖረን ግን አርሱ ይበቃናል ዳሩ ግን ባለጠጎች ሊሆኑ የሚፈልጉ በጥፊትና በመፍረስ ሰዎች በሚያሰጥምና በሚያሰንፍ በሚጎዳም በብዙ ምኞትና በፈተና ወጥመድም ይወድቃሉ፡፡- ገንዘብን መውደድ የክፋት ሁሉ ሥር ነውና አንዳንዶችም ይህን ሲመኙ ከፃይማኖት ተሳስተው በብዙ ሥቃይ ራሳቸውን ወጉ ብጳል፡፡ ፤1ጢሞ 6፡:6- [ዐ፡፡ ስለሆነም ከሥርቆት ኃጢአት ለመጠበቅ በሁሉ እያመስገንን "ኑሮዬ ይበቃኛል" ልንል ይገባናል፡፡ ፊልጵቁ፲፲፡፤ በጽድቅ የሚገኝ ጥቂት ነገር በዓመጽ ከሚገኝ ብዙ ትርፍ ይሻሳልና ምሳ 1፲6፡8::

አንግዲህ በተለያዩ ምክንያቶች በማወቅም ይሁን ባለማወቅ በስርቆት ላይ የተሰማራን ሰዎች መፍትሔው ንስሐ መሆኑን አውቀን አሁኑኑ ንስሐ - መግባት አለብን፡፡ ማቴ 6:3።ሖ፥ የበደልነውን ክሰን የቀማነውን መልሰን ዛሬውኑ ከሰውም ከእግዚአብሔርም ጋር መታረቅ ይገባናል፡፥ ዘሌ «4 ዘጸ 22:7-8 ምሳ 6:30-3] ለቃ 19-8 ፡::
```

#### Rank 10: `10commandments:chunk-0102:unit-01`

- parent chunk ID: `10commandments:chunk-0102`
- similarity_score: 0.8584825992584229
- page_start: 41
- page_end: 41
- unit token count: 71
- extraction method: ocr
- quality score: 85.33
- ground-truth relevant parent: yes

```text
ምኞትን መፈጸም ሰውን ከመመኘት አያድነውም የበለጠ የምኞትን ፆር ይጨምርበታል አእንጂ፡: በዓለማችን እንደምናየው ገንዘብ ለማግኘት ተመኝቶ ገንዝብን ያገኘሰው ተጨማሪ ገንዘብ ለመሰብሰብ ይመኛል እንጂ የሰበሰብኩት ይበቃኛል አይልም፡፡
```

#### Rank 11: `10commandments:chunk-0021:unit-01`

- parent chunk ID: `10commandments:chunk-0021`
- similarity_score: 0.8560740947723389
- page_start: 7
- page_end: 7
- unit token count: 194
- extraction method: ocr
- quality score: 84.45
- ground-truth relevant parent: no

```text
5.5

ስለዚህ ማንም ሰው አራሱን መግዛትና መካድ ከቻለ ዋነኛውን ጣዖት ከልቡናው አጠፋ ማለት ነው:፡፡

አሥራትን ለእግዚአብሔር ከመስጠት ይልቅ ለራሳችን ስንወስድ ሰንበትን ለሥጋዊ ፈቃድ መፈጸሚያ ስንጠቀም ራሳችንን መውደዳች አይደለምን? ፍላጎታችን ከእግዚአብሔር ትዕዛዝ ጋር በሚጋጭበት ጊዜ ፈቃዳችንን ከቋፈጸም ይልቅ« አርሱ እግዚአብሔር ሊልቅ እኔ ላንስ ያስፈልጋል» ያልን እንደሆነ ያን ጊዜ ራሳችንን በመካድ ሕይወታችንን ለዘለዓለም እንደምንጠብቃት እርግጠኞች እንሆናልን፡፡ ራስን ከማምለክ ነፃ አንድንወጣ ራሳችንን ለመካድ የሚያበቃ የጸጋ ስጦታን የሚያድል መድኃኔዓለም ክርስቶስ በቸርነቱ አመቤታችንን ቅድስት ድንግል ማርያም በአማላጅነቷ ይርዱን፡፡ አሜን
```

#### Rank 12: `10commandments:chunk-0061:unit-01`

- parent chunk ID: `10commandments:chunk-0061`
- similarity_score: 0.8560574054718018
- page_start: 23
- page_end: 23
- unit token count: 431
- extraction method: ocr
- quality score: 81.28
- ground-truth relevant parent: no

```text
ባታስጠነቅቀው ነፍሱም እንድትድን ከክፉ መንገዱ ይመለስ ዘንድ ለኃጢ አተኛው አስጠንቅቀህ ባትነግረው ያ ኃጢአተኛ በኃጢኣት ይሞታል፤ ደሙን ግን ከእጅህ እፈልጋለሁ: በማለት ስለኃላፊነታቸው አስገንዝቦአቸዋል፡፡ ሕዝ.3+16--18:፡፡

በመቀጠልም ኃጢአት ምን ያህል የከፋ መሆኑን ሲ ገልጥ «ነገር ግን አንተ ኃጢአተኛውን ብታስጠነቅቅ እርሱም ከኃጢአትና ከክፉ መንገዱ ባይመለስ+ በኃጢአቱ ይሞታል፥ሩ አንተ ግን ነፍስህን አድነሃል፡፡> በማለት የካህኑን የመጠበቅ ኃሳፊነት ዘርዝሮአል፡፡ ሕዝ.3+ 19፡- በመሆኑም ካህኑ ሕዝቡን ችላ በማለቱና እያንዳንዳቸውን ባለማስተማሩ ፣ ባለመጠበቁና ባለመከታተሉ በመንፈሳዊ ሕይወታቸው - ምውታን ስለሚሆኑ በእግዚአብሔር ዘንድ ስለእነዚህ ነፍሳት ከመጠየቅ አያምልጥም፡: ካህኑ የምአመናንን ነፍሳት ከፍርድ . ለማዳንና ለጽድቅ እንዲበቁም ለማድረግ በቀንም በሌሊትም ስለ እነርሱ ሕይወት በመጸምና በመጸለይ ኃላፊነቱን በሚገባ መወጣት ይጠበቅበታል፡፡ በራሱ ብቻ የግል ሕይወቱ መል ካም መሆኑ በቂ አይደለም: ስለዚህም በአደራ' 'ይጠብቃ ------ቸው-“ዘንድ-ለተሰጡት--የምእመናን-ነፍሳች-ግድ-የሌለው------.....---.

ካህን ለውድቀታቸውና ለዘለዓለማዊ ሞታቸው - ምክንያት በመሆኑ በእግዚአብሔር ዘንድ በዕዳ መጠየቁ ' አይቀርም፡፡

በተለይ የምእመናንን ሕይወት | ከእውነተኛው ሃይማኖት ለመለየት የሚጥሩ መናፍቃን ባሉበት የካህኑ ኃላፊነት የከበደ' ከመሆኑም በላይ 'በምእመናን ሞተ ነፍስ የተነሣ ተጠያቂነቱም ከፍተኛ ነው፡፡
```

#### Rank 13: `10commandments:chunk-0065:unit-02`

- parent chunk ID: `10commandments:chunk-0065`
- similarity_score: 0.8558905124664307
- page_start: 25
- page_end: 25
- unit token count: 183
- extraction method: ocr
- quality score: 79.22
- ground-truth relevant parent: no

```text
በመሆኑም ሰዎችን ከመንፈሳዊ ጉዞአቸው እንዳና ሰናክልና በፍርድ ቀን በእግዚአብሔር ፊት እንዳንጠየቅ መጠንቀቅ ያስፈልጋል፡፡ ክርስቶስ ስለፍርድ ቀን ባስተ ማረበት አንቀጽ ኃጢአት ከሠሩ ይልቅ ለኃጢአት ምክ ንያት የሆኑትን አስቀድሞ አውስቷቸዋል፤ «የሰው ልጅ መላእክቱን ይልካል+፥ ከመንግሥቱም እንቅፋትን ሁሉ አመ - ፃዓንም የሚያደርጉትን ይለቅማሉ፥ ወደ እቶነ እሳትም ይጥ ተ ሏቸዋል፤ በዚያ ልቅሶና ጥርስ ማፋጨት, ይሆናል፡> በማ ለት የሚያሰናክሉ ቅጣታቸው ከፍተኛ መሆኑን ገልጧል፡፡ ማቴ.13፥41--42፡:

ራስን መግደል ራስን መግደል ሌሎችን ከመግደል እኩል ነወው፡፡
```

#### Rank 14: `10commandments:chunk-0100:unit-02`

- parent chunk ID: `10commandments:chunk-0100`
- similarity_score: 0.8550570011138916
- page_start: 41
- page_end: 41
- unit token count: 228
- extraction method: ocr
- quality score: 85.33
- ground-truth relevant parent: no

```text
ለ. ስንፍና፡- ሰው ሆይ ለፍተህ ጥረህ ግረህ በላብህ ወዝ ብላ ለሚሰው አምላካዊ ትእዛዝ ጀርባቸውን የሰጡ ሰነፎች ሌላው ወጥቶ ወርዶ ያፈራውን ንብረት እያዩ ምነው ይህን ለእኔ ባደረገው አንዲህ ዓይነት ቤት ቢኖረኝ አቤት የእገሌን ሀብት ለእኔ ቢያደርገው እያሉ የሌላውን ንብረት የእነርሱ እንዲያደርገው ሌት ተቀን ሲያልሙ ይኖራሉ፡: የስንፍና ገመድ እጅና እግራቸውን ያሠራቸውን ሰዎች ለምኞት የተጋለጡ ብሎም በምኞት ፈረስ ተጭነው ወደ ኃጢአት ገደል የሚገቡ ናቸው፡፡

ሔ ራስን ከሌሎች ጋር ማነጻጸር:- ሰው አንደ ቤቱ እንጂ እንደ ጎረቤቱ አይኖርም ይባሳል፡፡ አንድ ሰው ሕይወቱን ሊመራ የሚገባው ከራሱ አቅም አንጻር መሆን ይኖርበታል፡፡ ዳሩ ግን የእርሱን ሕይወት ከሌሎች ጋር ማወዳደር ከጀመረ በምኞት ባሕር ውስጥ ጠልቆ መዳከር ይመጣል፡፡
```

#### Rank 15: `10commandments:chunk-0080:unit-02`

- parent chunk ID: `10commandments:chunk-0080`
- similarity_score: 0.8542911410331726
- page_start: 32
- page_end: 32
- unit token count: 376
- extraction method: ocr
- quality score: 83.12
- ground-truth relevant parent: no

```text
- ትክክል ባልሆነ መለኪያ ሚዛን ወዘተ መሸጥ፣ - . ለሠራተኛ ከሚገባው በታች እየከፈሉ ጉልበቱን መበዝበዝ፣ -- በሥራ ጊዜ በሰዓቱ አለመገኘት የሥራ ጊዜን በመዝናናት ማሳለፍ ሕጋዊ ያልሆነ የሕመም ፈቃድ ማውጣት ሥራን መሥራት እየቻሉ ከግዴለሽነት የተነሣ በተገቢው ጥራት አለመሥራት ከመግቢያ ሰዓት ዘግይቶ መግባትና ከመውጫ ሰዓት ሳያስፈቅዱ ቀድሞ መውጣት፣ - - ክሌላ የተገኘውን ፃሳብ እንደራስ አድርገ ማቅረብ ከሌላ የወሰዱትን ጥቅስ አባባል ድርሰት ወዘተ የፈጠሩት በማስመሰል ማቅረብ፣ - . ያልተፈቀደ የሰውን ምሥጢር በድብቅ መሰለልና ማየት፣ - የሰውን ገንዘብ ያለ አግባብ መበዝበዝ ወይም ጉቦ መቀበል፣ - ከሌባ ጋር መተባበር /ምሳ 29:2 ወዘተ በአጠቃላይ የእኛ ያልሆነውን ነገር ያለ አግባብ መውሰድ ሁሉ ስርቆት ነው፡፡: እንዲህም ሲልና የስርቆት ነገር ሲነሣ አኛን የማይመለከት የሚመስለን ሰዎች እንኖራለን፡፡፡- ይሁን አንጂ ከላይ አንደተመለከትናቸው ስርቆት የማይመለክተው ሰው አለ ማለት በጣም አስቸጋሪ ነወ፡: ለምሳሌ በስንፍና የሥራ ሰዓት አሳልፎ መግባት እና ሰዓቱ ሳይደርስ መውጣት ሳይታመሙ ታምሜአለሁ ያልሞተን ዘመድ ሞቷል አያሉ ከሥራ መቅረት ወዘተ ከመለመዱ የተነማ ብዙዎች ኃጢአት ሳይመስላቸው የሚፈጽሙት ነው፡ፎ፡ እንዲሁም አንድ የመሥሪያ ቤቱ የፅቃ ግዚ ክፍል ሠራተኛ የሆነ ሰው አሮጌ ቢገዛ ወይም ያልተገዛበትን ዋጋ በደረሰኝ ቢያሠራ የሰረቀ አይመስለውም፡፡
```

#### Rank 16: `10commandments:chunk-0105:unit-01`

- parent chunk ID: `10commandments:chunk-0105`
- similarity_score: 0.8542671203613281
- page_start: 42
- page_end: 43
- unit token count: 383
- extraction method: ocr
- quality score: 78.42
- ground-truth relevant parent: no

```text
በማሰናከል ከእግዚአብሔር ሰማጣሳትና በነፍሱም እንዲሞት ለማድረግ ነበርና መድኃኒታችን ኢየሱስ ክርስቶስም ስለአርሱ አርሱ ከመጀመሪያው ነፍሰ ገዳይ ነበረ ብሎአል። ዮሐ8፡4።«፣ የበቀል ስሜትም ከዚህ ምኞት ጋር የሚደመር ነው፡፡

የሰው ልጅ ከዚህ ክዳት ከምኞት ኃጢአት ተለይቶ ሰመኖር ውጊያውንም ሊቋቋም የሚችለው ለዚህ ዓለም እንግዳ መሆኑን በመገንዘብና ክንቱ የሆነውን የምኞት ምንጭ መናቅ መተው ሲቻለው ነው፡: "ሁሉ ከንቱ ነፍስንም አእንደመክተል ነውና እንዲሁም ደግሞ ዓለሙም ምኞቱም ያልፋሉና፡። መክ 1፲:፲ቁ፤1 ፲ዮሐ 2፡፲፲: የራስን ጥቅምና አርካታን ብቻ በማሰብ ላይ ተመሥርቶ በምኞት አሳት ከመቃጠል ይልቅ ሳያቋርጡ ስለ ሌሎች ሰዎች ማሰብን ሰውን ማፈቀርን አንዲሁም ሴሎችን በቸርነት የመርዳትን መንፈስ ገንዘብ ማድረግ ከምኞት የተሦሣ የሚፈጸመውን ኃጢአት ለመቋቋም ያስችላል፡፡ በዚህም ጸንተን ከምኞትም ተጠብቀን ለመኖር እንድንችል ቸሩ ፈጣሪያችን እግዚአብሔር ይርዳን:

አሥረኛው ትአዛዝ «ባል ሄፇጀራሀቻ ዳጳ2ደራዕሀሆ ውደድ» ዘሌ.19፥18

በዚሀ መጽሐፍ በመጀመሪያው ክፍል እንደተገለጠው ሁሉ በዘሌዋውያን 19-18 የተጻፈው «ባልንጀራህን እንደራ ስህ ውደድ» የሚለው ትእዛዝ በዘጸአት 20፥3-17 ከተዘረዘሩ ት ጋር ተዳምሮ ከአሠርቱ' ትእዛዛት መካከል አንዱ ነው፡፡
```

#### Rank 17: `10commandments:chunk-0097:unit-01`

- parent chunk ID: `10commandments:chunk-0097`
- similarity_score: 0.8540881872177124
- page_start: 40
- page_end: 40
- unit token count: 148
- extraction method: ocr
- quality score: 85.58
- ground-truth relevant parent: no

```text
ሽተው አንዲዋረዱ ጸጋቸውን እንዲገፈፍ አድርጓል። ዛሬም ሰው ያልተሰጠውን ክብር እንዲሻና ያንን ለማግኘትም እግዚአብሐርን በሚያሳዝን መልኩ እንዲሠማራ ያደርገዋል፡፡ ይህንንም የሚያደርገው የምናየወና የምንሰማውን መነሻ በማድረግ ነው፡፡

ምንም እንኳን ከላይ እንዳስቀመጥነው ምኞት መንፈሳዊ ሥጋዊና ሰይጣናዊ ተብሎ ቢከፈልም የዚህ ጽሑፍ ትኩረት ሰውን ከአግዚአብሔር ' ትእዛዝ ውጭ በሚያደርገው የምኞት ዓይነት ነው፡: ስለዚህ ከዚህ በኋላ ምኞት ስንል በሰዎች ዘንድ እንደ ኃጢአት የሚቆጠረውን ምኞት ማለታችን ነው፡፡
```

#### Rank 18: `10commandments:chunk-0111:unit-01`

- parent chunk ID: `10commandments:chunk-0111`
- similarity_score: 0.8532724380493164
- page_start: 46
- page_end: 46
- unit token count: 412
- extraction method: ocr
- quality score: 83.12
- ground-truth relevant parent: no

```text
ከመሥዋዕት፥ ማዳመጥም የአውራ በግ ስብ ከማቅረብ - ይበልጣል:> ያለው የእግዚአብሔርን ሕግ መፈጸም የከበረ መንፈሳዊ ዋጋ ያለውና እግዚአብሔርንም የሚያስደስት መሆኑን ለማስረዳት ነው: 1ሳሙ.15፥22፡ መድኃኒታችን ኢየሱስ ክርስቶስም - በመዋዕለ ትም ሀርቱ ባልንጀራን እንደመውደድ አግዚአብሔርን የሚያ ፡ ስደስተው ነገር - የሌለ መሆኑን ሲገልጥ «በፍጹም ልብ በፍጹም አእምሮም በፍጹም ነፍስም በፍጹም ኃይልም እርሱን መውደድ እግዚአብሔርን-፥ባልንጀራንም እንደራስ መውደድ በሙሉ ከሚቃጠል መሥዋዕትና ከሌላው መሥዋዕት ሁሉ የሚበልጥ ነው» በማለት አስተምሯል፡፡

ማር.12-+33:: | | እግዚአብሔርን መውደድና ባልንጀራንም እንደራስ መውደድ የሕግጋት ማሠሪያ ነው፤ ሕግጋትና ትእዛዛት ሁሉ በእነዚህ በሁለቱ ይጠቃለላሉ፡፡ ቅዱሳት መጻሕፍትም ይህንኑ ያረጋግጡልናል: ከነዚህም ማረጋገጫዎች መካከል ጌታችን ኢየሱስ ክርስቶስ ትእዛዛት ሁሉ እግዚአብሔርን በማ ፍቀርና ባልንጀራን እንደራስ በመውደድ የሚጠቃለሉ መሆኑን ከገለጸ በኋላ «ኦሪትና ነቢያት በእነዚህ በሁለቱ ትእዛዛት ጸኑ» በማለት የተናገረው. አንዱ ነው::

ማቴ.22-37-40:፡፡ | ቅዱስ ጳውሎስም በዚህ ቃለ ወንጌል መሠረት ለሮሜ ክርስቲያኖች በጻፈው መልእክት «አርስ በርሳችሁ ከመዋደድ በቀር ለማንም ዕዳ አይኑርባችሁ፥ ሌላውን የሚወድ ሕግን ፈጽሞታልና፡። አታመንዝር+ አትግደል፥ አትስረቅ፥ በውሸት አትመስክር+ አትመኝ የሚለው ከሌሳ
```

#### Rank 19: `10commandments:chunk-0092:unit-02`

- parent chunk ID: `10commandments:chunk-0092`
- similarity_score: 0.8531510233879089
- page_start: 38
- page_end: 38
- unit token count: 186
- extraction method: ocr
- quality score: 80.45
- ground-truth relevant parent: no

```text
ይህንን-' ኃጢአት አስጠያፊ የሚያደርገው ነገር 'አወዳሹ የሚያደንቀውን ሰው ሲያገኘው ማወደሱና በሌለበት ሥፍራ ደግሞ - የሚተቸው በመሆኑ ነው:: ስለዚህም ሰውን ባልዋለበት እንደዋለ፣ ያልሠራውን እንደሠራ፣ ያልሆነውን እንደሆነ አድርጎ ምስጋናና ውዳሴ እየሰጡ ማሞካሸት እውነተኛ መሠረት የሌለውና ያልተገባ ጥቅም ለማግኘት የሚደረግ ስለሆነ ከሐሰት ተነጥሎ አይታይም።፡ ከዚህ ሌላ ደግሞ ስለ አንድ ሰው ጠንካራ ጎን ሊነ ገሩ የሚገባቸውን በመተው ድካሙን ብቻ አጉልቶ በማ ሳየት ሌሎች ስለእርሱ ያሳቸውን አመለካከት ለመለወጥ መሞከር ግማሽ እውነት በመሆኑ እንደሐሰት የሚቆጠርና በኃጢአትነቱም የሚያስጠይቅ ነው: ሐሰት የተሰኘበት ምክንያትም ስለ ሰውየው የተሳሳተ መረጃ መስጠት ስለሆነ ነው::
```

#### Rank 20: `10commandments:chunk-0010:unit-01`

- parent chunk ID: `10commandments:chunk-0010`
- similarity_score: 0.8518103361129761
- page_start: 4
- page_end: 4
- unit token count: 298
- extraction method: ocr
- quality score: 84.55
- ground-truth relevant parent: no

```text
6-24

ማንም እግዚአብሔርን አመልካለሁ እያለ ገንዘብን ከመጠን በላይ የሚያፈቅር ከሆነ ራሱን ያሞኛል፡፡ ይህም የገንዘብን መገልገያነት መቃወም አይደለም፡፡ የገንዘብ አገልግሎትም ቢሆን ደግሞ ለአምልኮ ጣዖትና ለገቢረ ኃጢአት ከዋለ ገንዘብ አምላክሆፃ እየተመለከተ ነው ማለት ነው፡: በይበልጥ ደግሞ በአንዳች አገልግሎት ላይ ሳያውሉ ገንዘብን በማከማቸት የሚረኩ ሰዎች ለገንዘብ የተገዙና ገንዘብና አምላካቸው ያደረጉ ናቸው፡፡ እንደዚህ ዓይነት ሰዎች የሳንቲም ሽራፊ እአንድትወድቅባቸው የማይሹና በፈቃዳቸውም ገንዘብን የማይሰጡ (የማይመፀወቱ) ናቸው፡፡ እንደህ የሚያደርጋቸወ ፍቅረንዋይ ነው፡፡ ገንዘብን ከማንም በላይ ስሰሚወዱ እንደጣዖት ያመልኩታል፡፡ ጌታችን «ለእናንተ በምድር ላይ መዝገብ አትሰብስቡ» ሲል የተናገረው ለቪህ ነው፡፡ ማቴ. ፅ-19 የሰው ልጆች የሆንን እኛም የገንዘብ ፍቅር ወደልቡናችን እንዲገባና ሕንዲሠለጥን ከፈጣሪአችንም ጋር እንዳያጣላን መንገድ ከመክፈት በጽኑ ልንጠነቀቅ ይገባል፡፡ አንድ አባት መንፈሳዊ ልጃቸውን ሲመክሩ «ገንዘብ ካለህ በሥራ ሳይ አውለው፡፡

ገንዘብ ክሌለህ ግን ምንም አትሰብስ» ማለሰታቸወ አደገኛነቱን የሚያስረዳ ነው፡፡
```

### C. Parent-ranking analysis

Parent rank follows the first time each parent appears in the top 20. The official metric keeps only the first five parents.

| Parent rank | Parent chunk | Best unit rank | Best unit score | Pages | Ground-truth relevant |
| --- | --- | --- | --- | --- | --- |
| 1 | `10commandments:chunk-0101` | 1 | 0.8721902966499329 | 41–41 | no |
| 2 | `10commandments:chunk-0099` | 2 | 0.8673075437545776 | 40–41 | no |
| 3 | `10commandments:chunk-0098` | 3 | 0.867198646068573 | 40–40 | no |
| 4 | `10commandments:chunk-0094` | 4 | 0.8652994632720947 | 39–39 | no |
| 5 | `10commandments:chunk-0096` | 5 | 0.8636518120765686 | 40–40 | no |
| 6 | `10commandments:chunk-0081` | 6 | 0.8620849251747131 | 32–32 | no |
| 7 | `10commandments:chunk-0059` | 7 | 0.8604065179824829 | 22–23 | no |
| 8 | `10commandments:chunk-0104` | 8 | 0.8601696491241455 | 41–42 | no |
| 9 | `10commandments:chunk-0084` | 9 | 0.8600041270256042 | 33–33 | no |
| 10 | `10commandments:chunk-0102` | 10 | 0.8584825992584229 | 41–41 | yes |
| 11 | `10commandments:chunk-0021` | 11 | 0.8560740947723389 | 7–7 | no |
| 12 | `10commandments:chunk-0061` | 12 | 0.8560574054718018 | 23–23 | no |
| 13 | `10commandments:chunk-0065` | 13 | 0.8558905124664307 | 25–25 | no |
| 14 | `10commandments:chunk-0100` | 14 | 0.8550570011138916 | 41–41 | no |
| 15 | `10commandments:chunk-0080` | 15 | 0.8542911410331726 | 31–32 | no |
| 16 | `10commandments:chunk-0105` | 16 | 0.8542671203613281 | 42–43 | no |
| 17 | `10commandments:chunk-0097` | 17 | 0.8540881872177124 | 40–40 | no |
| 18 | `10commandments:chunk-0111` | 18 | 0.8532724380493164 | 46–46 | no |
| 19 | `10commandments:chunk-0092` | 19 | 0.8531510233879089 | 37–38 | no |
| 20 | `10commandments:chunk-0010` | 20 | 0.8518103361129761 | 4–4 | no |

- chunk-0102 has only one unit in the top 20. That unit is unit-01, search rank 10, similarity 0.858483. Nine earlier units belong to nine other parents, so the parent rank is 10. unit-02 and unit-03 of chunk-0102 are outside the top 20.

### D. False-positive analysis

Classifications cover units ranked above a relevant parent. Uncertain cases are marked.

- Rank 1, `10commandments:chunk-0101:unit-01`: **genuinely semantically related**. This unit ends with the same sentences that open the official relevant chunk. Preparation overlap copied «ምኞትን መፈጸም ሰውን ከመመኘት አያድነውም» and the money illustration into both parents. The unit also says desire is not pulled out of the heart by one satisfaction, and compares it to thirst. Under the official label it is not a relevant parent. In wording, it is the same claim.
- Rank 2, `10commandments:chunk-0099:unit-01`: **same topic but wrong answer**. Pages 40–41 say desire keeps fighting until what was desired is fulfilled, so the remedy is to flee before fulfilling it. Fulfillment is also said to lead into lying, theft, or killing. The vocabulary matches the question, but the claim is not that fulfillment increases desire.
- Rank 3, `10commandments:chunk-0098:unit-02`: **same topic but wrong answer**. Page 40 says desire fights without ceasing until what was desired is fulfilled, and therefore one should flee. That is the neighboring claim, not the claim that fulfillment increases desire.
- Rank 4, `10commandments:chunk-0094:unit-02`: **other**. Uncertain. Page 39 is still the lying chapter: silence is better than lying to escape pressure. The desire question does not use ሐሰት. A semantic reason for rank 4 is not clear from this unit.
- Rank 5, `10commandments:chunk-0096:unit-01`: **same topic but wrong answer**. Page 40 opens the ninth commandment, አትመኝ, and defines ምኞት as spiritual, bodily, or satanic. It is the right chapter and the right word, and it does not say that obtaining the desired thing increases desire.
- Rank 6, `10commandments:chunk-0081:unit-01`: **same topic but wrong answer**. Page 32 lists desire as a cause of theft. It shares ምኞት and the idea of wanting what is not one's own. It does not discuss whether fulfillment increases desire.
- Rank 7, `10commandments:chunk-0059:unit-01`: **other**. Uncertain. Pages 22–23 are the soul-killing exposition. It is not the desire chapter. Why it ranks seventh for this question is unclear from the passage.
- Rank 8, `10commandments:chunk-0104:unit-02`: **same topic but wrong answer**. Page 42 lists kinds of desire, including food, money, rank, and the fall of the devil. It belongs to the desire chapter and does not make the fulfillment-increases-desire claim.
- Rank 9, `10commandments:chunk-0084:unit-01`: **same terminology but different concept**. Page 33 quotes that people who want to be rich fall into harmful desire, and that love of money is a root of evil. It also teaches ኑሮዬ ይበቃኛል. The question's money illustration is nearby in topic, but this is the theft chapter's warning, not the page-41 claim.

### E. Relevant-passage analysis

1. Does the Amharic passage clearly answer the question? Yes. unit-01 says fulfilling desire does not free a person from desiring and increases it, then gives the money illustration. unit-02, which is outside the top 20, adds that satisfaction is only temporary.
2. Does the question wording differ from the passage? The question says ማግኘት and ከማጥፋት. The passage says መፈጸም and አያድነውም. The verbs differ. chunk-0101, ranked first, also contains የተመኘውን የፈጸመ, which is closer to the question than the short overlap unit alone.
3. Does the passage use indirect theological language? unit-02 teaches through Adam, Ahab, David, Solomon, and the sea that is never full. unit-01 states the claim directly.
4. Is the relevant unit short, long, or structurally unusual? The retrieved relevant unit is short, 71 tokens. It is the overlap copied from the end of chunk-0101. The parent's long explanatory unit is 406 tokens and was not retrieved in the top 20.
5. Is the relevant unit coherent? unit-01 is coherent: two complete sentences. It is structurally unusual only because it repeats the previous chunk's ending and stops before the examples.
6. What could make embedding retrieval difficult? The short unit has little text beyond a sentence that already appears, with more surrounding explanation, in the rank-1 unit. A duplicate short span is a weak distinct embedding.

### F. Most likely failure

**E. Ground-truth boundary, interacting with chunk overlap.** Confidence: high.

The approved relevant parent is only chunk-0102. The decisive sentences are also the ending of chunk-0101 because the preparation chunks overlap. chunk-0101 is unit rank 1 and parent rank 1. The retriever did find the claim. The metric counts a miss because that parent is not in the approved relevant set. Same-chapter desire passages then keep chunk-0102 itself at parent rank 10.

C is the right description of why the labeled parent is tenth. E is the right description of why the run is scored as a Recall@5 miss. The approved concept itself is supported by chunk-0102; this is a span-boundary observation, not a claim that the concept is wrong.

### G. Comparison with the original chunks

`chunk-0102`: The parent is one OCR chunk on page 41, about 1100 characters, split into three units of 71, 406, and 71 tokens. unit-01 repeats the end of chunk-0101 and is the only piece in the top 20, at rank 10. unit-02 contains the biblical examples and the temporary-satisfaction sentence and is absent from the top 20. unit-03 only introduces types of desire. The core sentence was not destroyed by the split. It was isolated from the examples, and the longer previous chunk that already contains it ranks first. Whether one embedding of the whole parent would have entered the top five is not known from this run.

Units of `10commandments:chunk-0102` after refinement:

`10commandments:chunk-0102:unit-01` — 71 tokens, pages 41–41

```text
ምኞትን መፈጸም ሰውን ከመመኘት አያድነውም የበለጠ የምኞትን ፆር ይጨምርበታል አእንጂ፡: በዓለማችን እንደምናየው ገንዘብ ለማግኘት ተመኝቶ ገንዝብን ያገኘሰው ተጨማሪ ገንዘብ ለመሰብሰብ ይመኛል እንጂ የሰበሰብኩት ይበቃኛል አይልም፡፡
```

`10commandments:chunk-0102:unit-02` — 406 tokens, pages 41–41

```text
አባታችን አዳም በገነት ያሉትን ዛፎች ሁሉ ከአንዲቱ በቀር አንዲያዝዝባቸው ሥልጣን ተሰጥቶት ነበር፡። በዚህ ባለመርካቱም ያቺን አንዲቱን ደግሞ ተመኛት ከፍሬዋ ለመብላትም ጓ5:፡ሪ፥ ሁሉ ያለው ንጉሠ አክዓብ የኢይዝራኤላዊውን የናቡቴን ትንሽ መሬት ተመኘ፡: ሰባት ሚስቶች የነበረው ዳዊት የወታደሩን /የባለሟሉን/ የኦርዮን ሚስት ተመኘ፡፡ ንጉሥ ሰሎሞንም ምኞቱን ለማርካት አስከ መጨረሻው ተዓዝ "ዓይኖቼንም ከፈለጉት ሁሉ አልከለክልኳቸውም በማለት መጨረሻ የሌለው ምኞቱን ገልጣል፡፡ መክ 2፡10: በዚህ ወጤትም በመቶዎች የሚቆሩ ሚስቶች ለእርሱ አደረገ በማይሞተው ቃሉም "ዓይን ከማየት አይጠግብም ጆሮም ከመስማት አይሞላም፡፥ ፈሳሾች ሁሉ ወደ ባሕር ይሄዳሉ፡፡ ባሕሩ ግን አይሞላም" በማለት ሊረካ የማይችል የምኞቱን ነገር ተናግሯል፡፡ መክ፲፡7ሀ8፡፣ በዚህም ምኞት ፈጽሞ እርካታ ማግኘት ጊዜያዊ ብቻ እንጂ ዳግመኛ ከመመኘት የሚገላግል መፍትሔ አለመሆኑን አስተምሮናል ለዚህ መፍትሔ የሚመኝ ሥጋን ራስን በመግዛት ልጓም መቆጣጠር ነው የሚሻለው ግን ፈጽሞ ከምኞት መሸሽ ነው፡፡ ያገባው ብዙም ሚስቶች የነበሩት ዳዊት እርካታን በፈለገና ራሱን መግዛት ባልተቻለው መጠን በምኞት ድል እንደተመታ ያላገባው ዮሴፍ በንጽሕና ሆኖ ራሱን በመግዛቱና ምኞትን ያሸነፋት የሸሹት ሰው እንጂ የተጋፈጡት አይደሉምና በጥበብ ሆኖ ከክፋ የሥጋ ምኞት መሸሽ መድኃኒት መሆኑን አውቀን ገንዘብ ልናደርገው ይገባናል፡፡
```

`10commandments:chunk-0102:unit-03` — 71 tokens, pages 41–41

```text
] የምኞት ዓይነቶች፡- ሐዋርያው ቅዱስ ጳውሎስም "ሥጋ በመንፈስ ላይ ይመኛል" በማለት ምኞት ከሥጋ ፈቃድ የሚመነጭ መሆኑን ተናግሯል፡፣ ገላ 5፡17፡፡ . ስለዚህ ምኞትን የሚያስከትል የሥጋ ፈቃድ ተዘርዝሮ የሚያበቃ አይደለም፡፡
```

## Conclusion

direct-05:

- relevant passage: `10commandments:chunk-0085` (page 34) and `10commandments:chunk-0089` (page 36)
- first relevant rank: unit rank 8, parent rank 8, `10commandments:chunk-0089:unit-02`
- strongest distractor: `10commandments:chunk-0013` at rank 1; the nearest same-chapter neighbor is `10commandments:chunk-0088`, 0.000098 similarity above the command unit
- likely failure category: C. Strong semantic distractors in the corpus
- confidence: medium

paraphrased-05:

- relevant passage: `10commandments:chunk-0102` (page 41)
- first relevant rank: unit rank 10, parent rank 10, `10commandments:chunk-0102:unit-01`
- strongest distractor: `10commandments:chunk-0101`, which already contains the same decisive sentences (145 overlapping characters)
- likely failure category: E. Ground-truth span boundary, with C explaining why the labeled parent is tenth
- confidence: high

## Overall recommendation

1. The retrieval units are only partly implicated. For direct-05, the command sentence was retrieved at unit rank 8; the neighbor phrase sits in a sibling unit outside the top 20. For paraphrased-05, the decisive sentence is intact both as a 71-token unit and inside the previous chunk. Unit segmentation is not the main reason both questions miss Recall@5.
2. Query formulation contributes to direct-05. ባልንጀራ matches the page-5 reputation passages more literally than the short command sentence. For paraphrased-05, ማግኘት and ማጥፋት differ from መፈጸም and አያድነውም, but the overlapping answer passage was still ranked first.
3. E5-small may be the limitation for direct-05. The top 20 similarities span about 0.014, and a same-chapter neighbor beats the command unit by less than 0.0001. That is a reason to test another embedding. It does not yet show that another model would separate these neighbors.
4. Testing BGE-M3 is justified now, on the same 182 units, the same query processing, and the same ground-truth-v2 labels. `direct-01` stays excluded.
5. There is no reason to change the current retrieval architecture before that comparison. Changing units, labels, or parent collapse would mix a model change with a data change. The page-41 overlap should be kept in mind when reading the next score, not edited before the run.

