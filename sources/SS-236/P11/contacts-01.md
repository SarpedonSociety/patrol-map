Parts (F) Ship contacts and (G) Aircraft contacts of the first part of the patrol, typed pages 10-15 of the report
(scan files Page12-Page17). Not raw Gemini output. Claude put the OCR working transcription (Qwen3-VL 8B checked
against Ternary Bonsai 27B) into the layout the converter reads on 2026-11-13, with the PSO's hand readings from the
scans of 13 November 2026 and Claude's reading of the page 14 scan (Page16.jpg) the PSO supplied. Readings that are
still uncertain are in ⟦ ⟧.

Layout changes, nothing else:
- The aircraft tables are printed with one contact per column and the fields down the side (four pages of seven
  contacts). They are turned here so each contact is a row, in the report's order, with its fields as typed. The
  report's row labels are kept as column headings, except that 'Time (Zone) I' becomes 'Time' with '(I)' in each
  cell, and the submarine's own speed, course and trim are headed 'S/M Speed', 'S/M Course' and 'S/M Trim' so the
  converter does not take them for the plane's.
- The report types the aircraft dates as month/day ('10/10'); '/44' is added so the converter can date them.
- The ship contact table prints time and date, and latitude and longitude, on two lines in one cell; they are
  joined on one line.
- Contact numbers the report prints only as column headings are given in the No. column.
- Positions the report types impossibly (for example 28-20 N among fixes at 25 N) are kept here as typed. The
  plotted estimates are in patrol.yml under row_estimates, with the evidence in review.yml.
- The moon rows (bearing, angle, illumination) are blank throughout the report and are left out.

Page 10
### (F) SHIP CONTACTS   P- Periscope.  R- Radar  SD- Day Sighting.  SN- Night Sighting.

| No. | Time Date | Lat. Long. | Type | Initial Range | Course | Speed | How Contacted | Remarks | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1. | 1220 (I) 10/10/44 | 24-30N 122-36E | Small Schooner | 15 Miles | 300T. | 6 | P | Too small for torpedo. | Date typed above the time in this row (10/10/44 1220 (I)). |
| 2. | 0019 (I) 10/12/44 | 24-55N 122-59E | Seven Sampans | 5200 yds. | 310 | 5 | R | Too small for torpedo. | |
| 3. | 0926 (I) 10/16/44 | 25-07N 122-09E | Small Trawler | 4000 yds. | 000 | 6 | P | Too small for torpedo. | |
| 4. | 1152 (I) 10/16/44 | 25-05N 122-09E | Two Sampans | 6000 yds. | Various | Various | P | Too small for torpedo. | Latitude has several characters typed and overstruck; read 25-05N by the PSO from the scan. A handwritten '?' beside it. |
| 5. | 0642 (I) 10/30/44 | 29-09N 132-00E | 1 Large AO 3 PC | 14 miles | 050 | 13 | SD | Attack #1. | Type read '1 Large 40' (Bonsai) for AO. The attack form gives the attack at 0800 (I), 29-18 N 132-06 E. |
| 6. | 30-21N 10/30/44 | 30-21N 132-55E | Six or More PC | Various | Various | Various | Various | Additional escorts for damaged AO | The time column is typed '30-21N' (the latitude repeated) over the date; the report gives no time (PSO, from the scan). Latitude in the position column read '3C-21N'. Remarks read 'Various escorts for damaged AO' (Qwen) / 'Additional / Various escorts for damaged 40' (Bonsai): check the scan. |
| 7. | 0210 (I) 11/1/44 | 26-27N 136-25E | 1 SS | 2500 yds. | ?? | 3 | SN | Fired two torpedoes at us. | Speed '3' as read (both reads). |

Page 11
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 10/10/44 | 1201 (I) | 24-15 | 122-37 | 2.5 | 315 | Per | 1 | BETTY | Tran. | Per | 4 | 2° | ND | 1 | 225 | 15 | 8000 | .1 |  |
| 2 | 10/10/44 | 1300 (I) | 24-18 | 122-36 | 2.5 | 354 | Per | 1 | IRVING | Tran. | Per | 15 | 1° | ND | 1 | 225 | 15 | 8000 | .1 |  |
| 3 | 10/10/44 | 1650 (I) | 24-33 | 122-22 | 2.3 | 340 | Fer | 1 | BETTY | Trans. | Per | 9 | 1° | ND | 1 | 090 | 15 | 4000 | .0 | Trim typed Fer (both reads). Type read BET_Y (Qwen). |
| 4 | 10/11/44 | 0735 (I) | 28-02 | 123-03 | 2.3 | 265 | Per | 1 | SALLY | Trans. | Per | 6 | 3° | ND | 1 | 160 | 15 | 6500 | .7 | Latitude typed 28-02 (PSO, from the scan); see row_estimates. The narrative calls AIRCON #4 a BETTY. |
| 5 | 10/12/44 | 0724 (I) | 24-40 | 123-42 | 2.3 | 237 | Per | 1 | BETTY | Trans. | Per | 10 | 2½° | ND | 2 | 150 | 15 | 8000 | .5 | Longitude typed 123-42 (PSO, from the scan); see row_estimates. |
| 6 | 10/12/44 | 1704 (I) | 24-20 | 122-44 | 2.3 | 240 | Per | 8 | SALLY | Bomb ? | Per | 12 | 1½° | ND | 3 | 120 | 15 | 6500 | .6 |  |
| 7 | 10/12/44 | 1755 (I) | 24-19 | 123-41 | 3.6 | 240 | Per | 6 | SALLY | Bomb | Per | 12 | 1° | ND | 3 | 120 | 15 | 4000 | .8 | Longitude typed 123-41 (PSO, from the scan); see row_estimates. S/M speed read 3,6 (Qwen) / 3.6 (Bonsai). |

Page 12
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 1-/14/44 | 1115 (I) | 22-46 | 122-34 | 2.6 | 230 | Per | 1 | BETTY | Pat. | Per | 9 | 1° | ND | 2 | 060 | 12 | 4000 | .6 | Date typed '1-/14' (PSO): 14 October. Latitude typed 22-46; see row_estimates. The narrative has AIRCON #8 at 0747 (I) on 14 October. |
| 9 | 10/14/44 | 1230 (I) | 24-48 | 122-11 | 10 | 270 | Surface | 1 | Unknown | Trans. | Sight | 8 | 3° | ND | 3 | 060 | 15 | 2000 | .5 | Time 1230 (PSO). The narrative has AIRCON #9 at 2232 (I) on 14 October (lights of a plane at night). |
| 10 | 10/15/44 | 0948 (I) | 28-35 | 121-49 | 2.7 | 190 | Per | 4 | BETTY | Bomb | Per | 8 | 2½° | ND | 2 | 180 | 15 | 2000 | 8 | Latitude typed 28-35; see row_estimates. Longitude 121-49: a 2 restruck as 1 on the original (PSO). Elevation typed 2°½. |
| 11 | 10/15/44 | 1242 (I) | 25-14 | 121-57 | 2.7 | 090 | Per | 1 | SALLY | Trans | Per | 8 | 3° | ND | 3 | 150 | 20 | 1500 | 5 |  |
| 12 | 10/15/44 | 1705 (I) | 25-10 | 122-05 | 2.7 | 090 | Per | 1 | SALLY | Rec. | Per | 3 | 2° | ND | 2 | 150 | 10 | 3000 | 6 |  |
| 13 | 10/17/44 | 1240 (I) | 25-07 | 122-08 | 2.7 | 180 | Per | 3 | NELL | Trans | Per | 6 | 3° | ND | 1 | 180 | 10 | 6000 | 6 | Date 10/17 (PSO). The narrative has AIRCON #13 (three NEILS) at 1240 (I) on 16 October. |
| 14 | 10/18/44 | 1545 (I) | 25-08 | 122-18 | 2.7 | 180 | Per | 1 | KITE | Trans | Per | 6 | 2° | ND | 2 | 150 | 10 | 3000 | 8 | Contact number read 15 (Qwen) / 14 (Bonsai); 14 by sequence. Date read 10/18 (both reads), but the narrative has AIRCON #14 (a KATE) at 1545 (I) on 17 October, and contact 15 on 10/18 is earlier in the day. Check the scan. |

Page 13
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | 10/18/44 | 1057 (I) | 25-00 | 122-18/30 | 2.0 | 225 | Per | 4 | BETTY | Trans | Per | 8 | 2° | ND | 2 | 040 | 15 | 3000 | 6 | Longitude typed 122-18/ with 30 written above (PSO, scan supplied): plotted as 122-18. |
| 16 | 10/20/44 | 0930 (I) | 25-19 | 122-00 | 2.0 | 099 | Per | 1 | SALLY | Trans | Per | 15 | ½° | ND | 2 | 040 | 15 | 2000 | 8 |  |
| 17 | 10/20/44 | 1115 (I) | 25-20 | 122-02/10 | 3.2 | 090 | Per | 1 | UNIDEN. |  | Per | 15 | ¼° | ND | 2 | 040 | 15 | 2000 | 8 | Longitude typed 122-02/ with 10 written above (PSO, scan supplied): plotted as 122-02. Probable mission blank. |
| 18 | 10/20/44 | 1230 (I) | 25-15 | 122-03 | 2.6 | 090 | Per | 1 | FRANCES | Pat. | Fer | 12 | 1° | ND | 1 | 040 | 20 | 2000 | ⟦9⟧ | How contacted typed Fer. Overcast read 9? (Qwen) / 95 (Bonsai). |
| 19 | 10/20/44 | 1257 (I) | 25-20 | 122-04 | 2.6 | 090 | Per | 1 | FRANCES | Pat. | Per | 12 | 1° | ND | 1 | 040 | 15 | 3000 | 9 |  |
| 20 | 10/20/44 | 1330 (I) | 25-20- | 122-07 | ⟦2.6⟧ | 090 | Per | 3 | SALLY | Trans | Per | 6 | 1° | ND | 1 | 040 | 10 | 3000 | 9 | S/M speed typed ',26'. |
| 21 | 10/20/44 | 1350 (I) | 25-21 | 122-10 | 2.6 | 090 | Per | 3 | NEILL | Trans | Per | 8 | 1° | ND | 1 | 040 | 10 | 3000 | 9 |  |

Page 14
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 22 | 10/20/44 | 1420 (I) | 25-21 | 122-12 | 2.6 | 090 | per | 2 | NEIL | Trans | Per | 8 | 1° | ND | 1 | 040 | 10 | 3000 | 9 | Read from the scan (Page16.jpg). |
| 23 | 10/20/44 | 1435 (I) | 25-22 | 122-14 | 2.6 | 090 | Per | 5 | SALLY | Trans | Per | 5 | 1° | ND | 1 | 040 | 10 | 2000 | 9 | Read from the scan (Page16.jpg). |
| 24 | 10/20/44 | 1455 (I) | 28-20 | 122-13 | 2.6 | 090 | Per | 3 | MAVIS | Pat | Per | 4 | 3° | ND | 1 | 040 | 10 | 2000 | 9 | Latitude typed 28-20 (scan); see row_estimates. |
| 25 | 10/20/44 | 1625 (I) | 25-15 | 122-15 | 2.6 | 270 | Per | 1 | TESS | Trans | Per | 6 | 2° | ND | 2 | 040 | 10 | 2000 | 8 | Read from the scan (Page16.jpg). |
| 26 | 10/20/44 | 1738 (I) |  |  | 2.6 | 270 | Per | 1 | Uniden. JILL ? | Pat | Per | 6 | 2° | ND | 2 | 040 | 10 | 200 | 7 | No position recorded (PSO, from the scan); see row_estimates. Cloud height typed 200. |
| 27 | 10/22/44 | 1112 (I) | 25-13/05 | 122-02/30 | 2.0 | 270 | Per | 7 | SALLY | Bomb | Per | 12 | 1° | ND | 2 | 030 | 20 | 5000 | 8 | Typed 25-13/ with 05 above, and 122-02/ with 30 above (scan): plotted as 25-13, 122-02. |
| 28 | 10/22/44 | 1710 (I) | 25-13 | 122-05 | 2.6 | 090 | Per | 5 | 1 Med.Bomber 4 Int. Unidentified. | Unk | Per | 6 | 1° | ND | 2 | 030 | 15 | 3000 | 5 | Read from the scan (Page16.jpg). |

Page 15
### (G) AIRCRAFT CONTACTS

| No. | Date | Time | Lat. | Long. | S/M Speed | S/M Course | S/M Trim | Number | Type | Probable Mission | How Contacted | Initial Range | Elevation Angle | Range & Relative Bearing of Plane When It Detected S/M | Sea State (Beaufort) | Sea Direction (Rel) | Visibility (Miles) | Clouds Height in Ft. | Clouds Percent Overcast | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | 10/23/44 | 1245 (I) | 125-10 | 123-35 | 2.6 | 240 | Per | 1 | SALLY | Trans | Per | 12 | 2° | ND | 1 | 060 | 20 | 6000 | .4 | Date 10/23 with a slash through the 3 (PSO; read 10/26 by both models). Latitude typed 125-10; see row_estimates. |
| 30 | 10/23/44 | 1317 (I) | 125-10 | 123-35 | 2.6 | 210 | Per | 1 | MAVIS | Trans | Per | 15 | 1° | ND | 1 | 060 | 20 | 6000 | .4 | Type typed M.VIS. Latitude typed 125-10; see row_estimates. |
| 31 | 10/23/44 | 1440 (I) | 125-10 | 123-35 | 2.6 | 210 | Per | 1 | MAVIS | Trans | Per | 14 | 1° | ND | 1 | 060 | 15 | 6000 | .6 | Time 1440 (PSO; read 1140 by Bonsai). Type typed M.VIS. Latitude typed 125-10; see row_estimates. |
| 32 | 10/24/44 | 1205 (I) | 125-03 | 123-40 | 2.6 | 240 | Per | 1 | BETTY | Trans | Per | 5 | 1° | ND | 1 | 060 | 15 | 5000 | .5 | Latitude typed 125-03; see row_estimates. The narrative types this contact AIRCON #33. |
| 33 | 10/25/44 | 1450 (I) | 25-40 | 124-40 | 11.7 | 000 | Surf | 1 | UNIDENT. | Trans | Sight | 20 | 4° | ND | 1 | 060 | 30 | 8000 | .1 | Time 1450 (PSO; read 1150 by Bonsai). |
| 34 | 10/27/44 | 1109 (I) | 24-56 | 122-34 | 10.8 | 170 | P'r | 1 | BETTY | Patrol | Sight | 3 | 50° | ?? | 2 | -- | 20 | 5000 | .5 | Type typed BETTER (Qwen) / BETTR (Bonsai); BETTY in the narrative. Trim typed P'r. |
| 35 | 10/27/44 | 1759 (I) | 24-45 | 122-21 | 10.0 | 005 | per | 4 | UNIDENT. NELL ? | Trans. | Sight | 10 | 15° | ND | 1 | 270 | 25 | --- | .1 | Not in the narrative. |

Remarks: NOTE: Numerous friendly planes that were sighted enroute to and from station are not listed. SD was not used at any time.

Type of S/M Camouflage on this patrol - Modified Grey. (Printed under each aircraft table.)
