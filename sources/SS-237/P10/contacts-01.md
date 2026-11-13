Parts (F) Ship contacts and (G) Aircraft contacts of the first part of the patrol, typed pages 22-27 of the report
(scan files WP10.23-WP10.28). Not raw Gemini output. Claude put the OCR working transcription (Qwen3-VL 8B checked
against Ternary Bonsai 27B) into the layout the converter reads on 2026-11-13, with the PSO's hand readings from the
scans of 13 November 2026. Bonsai's read of pages 22 and 24 stops partway, so most figures on page 24 (aircraft
contacts 8-14) rest on Qwen's read alone. Readings that are still uncertain are in ⟦ ⟧.

Layout changes, nothing else:
- The ship contact table prints time and date, and latitude and longitude, on two lines in one cell; they are joined
  on one line. The column order is a working layout (the headings are read 'Est Initial Course' (Qwen) / 'Initial
  Est Course' (Bonsai)); the courses of contacts 1-8 were read by neither model and are left blank.
- The aircraft tables are printed with one contact per column and the fields down the side (four pages of seven
  contacts, then two). They are turned here so each contact is a row, in the report's order, with its fields as
  typed. The report's row labels are kept as column headings; the submarine's own speed, course and trim are headed
  'S/M Speed', 'S/M Course' and 'S/M Trim' so the converter does not take them for the plane's.
- The aircraft tables head the time row 'Time (Zone)' but print no zone letter. Each time is given here with the zone
  of the narrative entry for the same plane contact: (L) for contact 1 (3 October, before SAIPAN), (I) for the rest.
- The aircraft dates are typed '3 Oct.' and so on, without a year; the converter takes 1944 from patrol.yml.
- Positions the report types impossibly are kept here as typed. The plotted estimates are in patrol.yml under
  row_estimates, with the evidence in review.yml.
- The moon rows (bearing, angle, illumination) are blank throughout and are left out.

Page 22
### (F) SHIP CONTACTS

| No. | Time Date | Lat. Long. | Type | Est. Course | Initial Range | Speed | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1405 (I) 10-8-44 | 21-11 N 130-41 E | Large Sampan |  | 20,000 | 4 kts. | Course not read. |
| 2 | 2203 (I) 10-10-44 | 24-31 N 122-20 E | 2 Sampans |  | - | ? | Course not read. A sound contact (narrative 2203 (I)); aircraft contact 10, five minutes earlier, is at 24-24.8 N 122-21 E. |
| 3 | 0320 (I) 10-12-44 | 24-50 N 122-23 E | About 10 Sampans |  | 8,500 | 7 | Course not read. Range 8,500 (PSO). |
| 4 | 1005 (I) 10-18-44 | 25-20 N 122-37 E | SHIGURE class Destroyer |  | 10,000 | 15 | Course not read. Dated 10-18-44 as typed (PSO); the narrative and the 1st endorsement put this contact on 19 October. See row_estimates. |
| 5 | 1328 (I) 10-18-44 | 25-15 N 122-48 E | 2 ATAGO CA's, 1 NATORI CL, 2 DD Leaders or CL's, Several FUBUKI DD's |  | 16,000 | 15 | Course not read. Dated 10-18-44 as typed (PSO); see contact 4. Range 16,000 (PSO); the narrative has 18,000 yds. at first sighting. |
| 6 | 1400 (I) 10-24-44 | 25-16 N 123-50 E | BUENOS AIRES MARU Hospital Ship |  | 20,000 | 10 | Course not read. |
| 7 | 0836 (I) 10-26-44 | 24-07 N 125-41 E | 2 BB's |  | 50,000 | 19 | Course not read. Latitude 24-07 N (PSO; the 0 could be read as a 6 but is not); longitude read 126-41 by Qwen, 125-41 by Bonsai and the PSO. The narrative heading reads 24-97 / 24-57 N 125-41 E. |
| 8 | 0540 (I) 10-27-44 | 24-39 N 123-36 E | 5 Sampans |  | 8,000 | 2 | Course not read. Range 8,000 (PSO). |
| 9 | 0912 (I) 10-29-44 | 26-10 N 130-39 E | 8 Sampans | 160°T | 12,000 | 4 | Course from Bonsai. The narrative has 6 tuna boats and two escorts. |
| 10 | ⟦0710⟧ (I) 10-30-44 | 29-29 N 132-05 E | 1 converted Tanker 4 escorts | 050°T | 24,000 | 16 | Time read 0718 (Qwen) / 0710 (Bonsai); the narrative has 0710. Course from Bonsai. The narrative heading numbers this contact #9. |

Page 23
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Minutes Since Last SD Radar Search | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3 Oct. | 0712 (L) | 16-32N | 145-50E | 17 | 255 | Sur. | - | 1 | LIBER. | Patrol | Sight | 5000 | 20° | ⟦- 520⟧ | 4 | 120 | 3 | 3000 | 190% | Zone (L) from the narrative (0712 (L), 3 October). The detection cell read '520' (Qwen) / '320' (Bonsai). Overcast typed 190% in both reads. |
| 2 | 6 Oct. | 1025 (I) | 18-25N | 145-50E | 11 | 310 | Sur. | - | 1 | LIBER. | Patrol | Sight | 4000 | 10° | ⟦- 090⟧ | 9 | 290 | 3 | 1500 | ⟦106%⟧ | Overcast read 106% (Qwen) / 100% (Bonsai). Longitude 145-50E in both reads, the same as contact 1: see review.yml. |
| 3 | 7 Oct. | 0900 (I) | 19-10N | 140-15E | 13 | 290 | Sur. | - | 1 | LIBER. | Patrol | Sight | 8000 | 5° | Not Det. | 8 | 280 | 3 | 1200 | 80% | See review.yml (140-15E against contact 4 at 137-17E 4 hours 50 minutes later). |
| 4 | 7 Oct. | 1350 (I) | 19-20N | 137-17E | 13 | 290 | Sur. | - | 1 | LIBER. | Patrol | Sight | 9000 | 8° | ⟦90 Stbd. Exch. Rec. Sig.⟧ | 7 | 280 | 5 | 1200 | 90% | The narrative has recognition signals exchanged with this plane. |
| 5 | 8 Oct. | 0838 (I) | 20-45N | 131-57E | 16 | 290 | Sur. | ⟦11 min.⟧ | 1 | ⟦4 Eng. Patrol⟧ | Patrol | Sight | 22000 | 2° | ⟦5,000 Not Det.⟧ | 5 | 280 | 10 | 3000 | 70% | The type row reads 'LIBER. LIBER. LIBER. LIBER. 4 Eng. Patrol - Single Engine' across seven columns (both reads); how its last four entries fall among contacts 5-7 is uncertain, as is the column of '11 min.' (Qwen puts it under 5; the narrative has contact 6 on the SD). Check the scan. |
| 6 | 8 Oct. | 0859 (I) | 20-46N | 131-55E | 16 | 290 | Sur. | - | 1 | ⟦-⟧ | Patrol | Sight | 28000 | - | Closing fast | 5 | 280 | 10 | 3000 | +70% | See contact 5. The narrative: 'Plane (PLANE CONTACT #6) on S.D.' |
| 7 | 8 Oct. | 1040 (I) | 20-50N | 131-33E | 17 | 286 | Sur. | - | 1 | ⟦Single Engine⟧ | Unk | Sight | 20000 | 4° | Not Det. | 3 | 280 | 15 | 3000 | 30% | See contact 5. |

Page 24
### (G) AIRCRAFT CONTACTS (Cont'd.)

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Minutes Since Last SD Radar Search | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 8 Oct. | 1415 (I) | 21-12N | 130-55E | 17 | 180 | Sur. | - | 1 | Single | Unk | Sight | 5000 | 15° |  | 3 | 300 | 20 | 3000 | 20% | Page 24 rests on Qwen's read (Bonsai's stops after the speed row). Ship contact 1, ten minutes earlier, is at 21-11 N 130-41 E, 13 miles west. |
| 9 | 9 Oct. | 1030 (I) | 22-49N | 125-50E | 17 | 286 | Sur. | - | 3 | Single | Unk | Sight | 5000 | 65° |  | 3 | 300 | 20 | 3000 | 20% | Qwen's read only (see contact 8). |
| 10 | 10 Oct. | 2158 (I) | 24-24.8 | 122-21E | 8 | 035 | Sur. | Pick Up on SJ | 1 | Unk | Patrol | Radar | 6000 | - |  | 3 | 067 | 5 | 5000 | 60% | Qwen's read only (see contact 8). |
| 11 | 12 Oct. | 0705 (I) | 25-07N | 122-18E | 11 | 270 | Sur. | - | 1 | Tw.Eng. | Patrol | Sight | 12000 | 5° |  | 3 | 235 | 20 | 5000 | 30% | Qwen's read only (see contact 8). |
| 12 | 12 Oct. | 0710 (I) | 25-07N | 122-18E | 3 | 270 | Sub. | - | 1 | Si.Eng. | Patrol | Per. | 8000 | 10° |  | 3 | 235 | 20 | 5000 | 30% | Qwen's read only (see contact 8). |
| 13 | 13 Oct. | 0715 (I) | 25-08.5 | 122-22E | 3 | 180 | Sub. | - | 2 | Betty | Patrol | Per. | 10000 | 5° |  | 4 | 030 | 10 | 5000 | 40% | Qwen's read only (see contact 8). |
| 14 | 14 Oct. | 0920 (I) | 25-18.2 | 122-01E | 3 | 300 | Sub. | - | 9 | Si.Eng. | Unk | Per. | 10000 | 30° |  | 3 | 235 | 10 | 3000 | 20% | Qwen's read only (see contact 8). The detection row is blank in Qwen's read; Bonsai's has 'Closing ... Fast' for some contact on this page. |

Page 25
### (G) AIRCRAFT CONTACTS (Cont'd.)

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Minutes Since Last SD Radar Search | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | 15 Oct. | 1445 (I) | 24-56.1 | 122-53E | 3 | 025 | Sub. | - | 1 | T.W.Eng.(Betty) | Patrol | Per. | 6000 | 3° | - | ⟦2⟧ | 045 | 20 | 8000 | 10% | Sea state row read '2 3 2 3 3 3 3 3' (Qwen) / '2 2 2 3 3 3 3' (Bonsai). |
| 16 | 15 Oct. | 1658 (I) | 25-05.5 | 122-03E | 3 | 025 | Sub. | - | 1 | T.W.Eng.(Betty) | Patrol | Per. | 10000 | 3° | - | ⟦3⟧ | 045 | 20 | 8000 | 10% | See contact 15 (sea state). Longitude 122-03E in both reads, 46 miles from contact 15 in 2 hours 13 minutes submerged: see review.yml. |
| 17 | 19 Oct. | 1232 (I) | 25-20.4 | 122-09E | 3 | 300 | Sub. | - | 1 | Si.Eng. | Patrol | Per. | 10000 | 1° | - | ⟦2⟧ | 065 | 15 | 10000 | 5% | 1232 and 25-20.4 N 122-09 E (PSO, from the scan; Qwen read the longitude 123-09). The narrative puts PLANE CONTACT #17, the float plane over the task force, at 1332 (I). Bonsai reads the type 'F1.Type. Si.Eng.' (float type). See review.yml. |
| 18 | 20 Oct. | 1223 (I) | 25-00N | 122-39E | 3 | 090 | Sub. | - | 1 | Betty | Patrol | Per. | 20000 | 5° | - | 3 | 060 | 10 | 10000 | 10% | Latitude 25-00N (PSO: a faded 0 read as C by Qwen). See review.yml. |
| 19 | 20 Oct. | 1300 (I) | 25-04N | 122-27E | 3 | 090 | Sub. | - | 1 | Betty | Patrol | Per. | 15000 | 6° | - | 3 | 060 | 10 | 10000 | 10% | See review.yml. |
| 20 | 20 Oct. | 1343 (I) | 25-14N | 122-13E | 3 | 270 | Sub. | - | 3 | Betty's | Unk | Per. | 20000 | 5° | - | 3 | 060 | 10 | 10000 | 10% | |
| 21 | 20 Oct. | 1500 (I) | 25-13N | 122-13E | 3 | 270 | Sub. | - | 3 | Mavis' | Unk | Per. | 20000 | 20° | - | 3 | 060 | 10 | 10000 | 10% | SILVERSIDES' aircraft contact 24 (three Mavis, 1455 (I)) is the same three planes. |

Page 26
### (G) AIRCRAFT CONTACTS (Cont'd.)

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Minutes Since Last SD Radar Search | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 22 | 22 Oct. | 1015 (I) | 25-19 N | 122-10E | 3 | 305 | Sub. | - | 1 | Betty | Patrol | Per. | 10000 | 5° | - | 4 | 055 | 15 | 15000 | 5% | |
| 23 | 22 Oct. | 1545 (I) | 25-17N | 122-17W | 3 | 100 | Sub. | - | 3 | ⟦Zeke, 2 Betty's⟧ | Patrol | Per. | 10000 | 5° | - | 4 | 055 | 15 | 15000 | 5% | Longitude printed W on the original (PSO); E is meant: see row_estimates. Type read 'Betty's' (Qwen) / 'Zeke, 2 Betty's' (Bonsai). |
| 24 | 23 Oct. | 1108 (I) | 25-15N | 124-05W | 14 | 060 | Sur. | 38 | 2 | Mavis' | Patrol | Sight | 15000 | 1° | - | 3 | 060 | 15 | 50000 | 80% | Longitude printed W on the original (PSO); E is meant: see row_estimates. |
| 25 | 26 Oct. | 0900 (I) | 24-07N | 125-41E | 17 | 075 | Sur. | - | 1 |  | ⟦Anti Sub. Sweep⟧ | Per. | 30000 | 5° | - | 1 | 060 | UN | 10000 | 10% | Qwen reads 'Anti.Sub.' in the type row and 'Sweep' as the mission; Bonsai reads the mission 'Anti Sub Sweep'. The plane over the task force (narrative, 0836 (I)). |
| 26 | 27 Oct. | 0647 (I) | 24-38N | 123-35E | 3 | 120 | Sub. | - | 1 | Mavis | Patrol | Per. | 18000 | 5° | - | 1 | 060 | 20 | 6000 | 10% | |
| 27 | 28 Oct. | 0916 (I) | 23-43N | 124-47E | 16 | 090 | Sur. | - | 1 | - | Patrol | Sight | 18000 | 5° | - | 2 | 060 | UN | 10000 | 30% | |
| 28 | 1 Nov. | 1417 (I) | 23-49N | 137-30E | 16 | 155 | Sur. | - | 2 | B-24 | ⟦Own Air Cover.⟧ | Sight | 12000 | 3° | - | 1 | 090 | UN | 10000 | 5% | Mission read 'Cover.' (Qwen) / 'Own Air Cover.' (Bonsai). |

Page 27
### (G) AIRCRAFT CONTACTS (Cont'd.)

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Minutes Since Last SD Radar Search | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | 2 Nov. | 0803 (I) | 20-01N | 139-56E | 16 | 155 | Sur. | - | 2 | PB-2Y | Own Air Cover. | Sight | 20000 | 3° | - | 1 | 090 | UN | 10000 | 5% | |
| 30 | 2 Nov. | 1905 (I) | 17-50N | 141-05E | 15 | 133 | Sur. | - | 2 | LIBER. | Own Air Cover. | ⟦Gr. flare SJ Rad.⟧ | 20000 | 1° | - | 1 | 090 | UN | 10000 | 5% | How contacted read 'SJ Rad' (both reads); Bonsai places 'Gr. flare' in this column. The narrative has a green flare and a pip on SJ at 1900. |
