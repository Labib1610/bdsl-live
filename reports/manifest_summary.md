# BdSLW60 manifest summary

- Total trials: **9267**
- Unique words: **60**
- Unique signers: **18**
- Total anomalies logged: **409**

## Trials per signer

| signer | trials |
|---|---|
| U1 | 945 |
| U2 | 744 |
| U3 | 583 |
| U4 | 637 |
| U5 | 600 |
| U6 | 815 |
| U7 | 107 |
| U8 | 639 |
| U9 | 656 |
| U10 | 383 |
| U11 | 771 |
| U12 | 655 |
| U13 | 621 |
| U14 | 112 |
| U15 | 655 |
| U16 | 97 |
| U17 | 116 |
| U18 | 131 |

## Trials per word

| word | label_idx | trials |
|---|---|---|
| W1 | 0 | 164 |
| W2 | 1 | 175 |
| W3 | 2 | 163 |
| W4 | 3 | 161 |
| W5 | 4 | 158 |
| W6 | 5 | 162 |
| W7 | 6 | 167 |
| W8 | 7 | 177 |
| W9 | 8 | 172 |
| W10 | 9 | 161 |
| W11 | 10 | 159 |
| W12 | 11 | 172 |
| W19 | 12 | 154 |
| W20 | 13 | 156 |
| W37 | 14 | 161 |
| W38 | 15 | 161 |
| W39 | 16 | 170 |
| W40 | 17 | 155 |
| W41 | 18 | 164 |
| W42 | 19 | 160 |
| W43 | 20 | 138 |
| W44 | 21 | 160 |
| W45 | 22 | 151 |
| W46 | 23 | 159 |
| W47 | 24 | 153 |
| W48 | 25 | 158 |
| W49 | 26 | 169 |
| W50 | 27 | 166 |
| W91 | 28 | 130 |
| W92 | 29 | 136 |
| W93 | 30 | 127 |
| W94 | 31 | 123 |
| W95 | 32 | 123 |
| W96 | 33 | 129 |
| W97 | 34 | 123 |
| W98 | 35 | 120 |
| W99 | 36 | 130 |
| W100 | 37 | 118 |
| W111 | 38 | 113 |
| W112 | 39 | 130 |
| W211 | 40 | 130 |
| W212 | 41 | 126 |
| W213 | 42 | 133 |
| W214 | 43 | 120 |
| W215 | 44 | 118 |
| W216 | 45 | 145 |
| W217 | 46 | 134 |
| W218 | 47 | 145 |
| W219 | 48 | 124 |
| W220 | 49 | 140 |
| W351 | 50 | 179 |
| W352 | 51 | 203 |
| W353 | 52 | 171 |
| W354 | 53 | 197 |
| W355 | 54 | 186 |
| W356 | 55 | 199 |
| W357 | 56 | 181 |
| W358 | 57 | 186 |
| W359 | 58 | 219 |
| W360 | 59 | 203 |

## Orientation distribution

| orientation | trials |
|---|---|
| RightHand | 7663 |
| LeftHand | 1604 |

## FPS distribution

| fps | trials |
|---|---|
| 15 | 1631 |
| 24 | 4206 |
| 30 | 3430 |

## Duration histogram (10 buckets)

```
[ 0.25,  0.77) s |  1775 | ########
[ 0.77,  1.29) s |  2917 | #############
[ 1.29,  1.80) s |  2188 | #########
[ 1.80,  2.32) s |  1289 | ######
[ 2.32,  2.84) s |   597 | ###
[ 2.84,  3.36) s |   291 | #
[ 3.36,  3.88) s |   119 | #
[ 3.88,  4.40) s |    48 | 
[ 4.40,  4.92) s |    30 | 
[ 4.92,  5.43) s |    13 | 
```

## Anomalies

| kind | count |
|---|---|
| bad_filename | 4 |
| n_frames_out_of_range | 275 |
| no_of_trials_mismatch | 37 |
| no_of_trials_unparsable | 93 |

<details><summary>Full anomaly list</summary>

- `bad_filename` [W357-358] U18W358FL (skipped 10 trial(s))
- `bad_filename` [W357-358] U1W357F_1 (skipped 9 trial(s))
- `bad_filename` [W357-358] U1W357F_2 (skipped 9 trial(s))
- `bad_filename` [W357-358] U1W357F_3 (skipped 12 trial(s))
- `n_frames_out_of_range` [W1-2] U12W2F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W1-2] U1W2F/LeftHand trial 14: n_frames=8
- `n_frames_out_of_range` [W1-2] U1W2F/LeftHand trial 16: n_frames=9
- `n_frames_out_of_range` [W1-2] U2W2F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W1-2] U2W2F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W1-2] U2W2F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W1-2] U3W2F/RightHand trial 16: n_frames=8
- `n_frames_out_of_range` [W1-2] U5W2F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W1-2] U5W2F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W1-2] U5W2F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W1-2] U5W2F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W111-112] U12W112F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W111-112] U12W112F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W111-112] U15W112F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W111-112] U15W112F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W111-112] U15W112F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W111-112] U15W112F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W111-112] U15W112F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W111-112] U4W112F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W111-112] U4W112F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W111-112] U6W111F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W111-112] U6W111F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 1: n_frames=8
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W111-112] U6W112F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 1: n_frames=8
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W19-20] U4W20F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W211-212] U2W211F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W215-216] U8W216F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W215-216] U8W216F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W215-216] U8W216F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W215-216] U8W216F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W215-216] U9W216F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 13: n_frames=9
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 14: n_frames=9
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 17: n_frames=8
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 18: n_frames=8
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 20: n_frames=9
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 4: n_frames=9
- `n_frames_out_of_range` [W217-218] U11W218F/LeftHand trial 8: n_frames=9
- `n_frames_out_of_range` [W217-218] U12W218F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 11: n_frames=9
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 14: n_frames=8
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W217-218] U1W218F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W217-218] U8W218F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W217-218] U8W218F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W217-218] U9W218F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 14: n_frames=8
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W219-220] U11W220F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W219-220] U13W220F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W219-220] U1W220F/RightHand trial 14: n_frames=8
- `n_frames_out_of_range` [W359-360] U11W359F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W359-360] U11W359F/RightHand trial 12: n_frames=8
- `n_frames_out_of_range` [W359-360] U11W359F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W359-360] U11W359F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W359-360] U11W359F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 1: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 5: n_frames=7
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 7: n_frames=7
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W359-360] U12W359F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W359-360] U13W359F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W359-360] U13W359F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W359-360] U14W359F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W359-360] U14W359F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W359-360] U15W359F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W359-360] U15W359F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W359-360] U15W359F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W359-360] U15W359F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W359-360] U16W359F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W359-360] U16W359F/RightHand trial 1: n_frames=8
- `n_frames_out_of_range` [W359-360] U16W359F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W359-360] U16W359F/RightHand trial 3: n_frames=7
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 11: n_frames=9
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 14: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 15: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 16: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W359-360] U18W359F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 11: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 14: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 15: n_frames=8
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 16: n_frames=8
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 17: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W359-360] U3W359F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W359-360] U4W359F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W359-360] U5W359F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W359-360] U6W359F/RightHand trial 17: n_frames=9
- `n_frames_out_of_range` [W359-360] U7W359F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W359-360] U8W359F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W359-360] U9W359F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W359-360] U9W359F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 12: n_frames=7
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 13: n_frames=5
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 14: n_frames=5
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 15: n_frames=5
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W37F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 0: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 11: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 12: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 13: n_frames=9
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W37-38] U3W38F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 6: n_frames=6
- `n_frames_out_of_range` [W37-38] U4W37F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W39-40] U1W40F/LeftHand trial 11: n_frames=9
- `n_frames_out_of_range` [W39-40] U1W40F/LeftHand trial 9: n_frames=9
- `n_frames_out_of_range` [W39-40] U3W40F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W39-40] U3W40F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W39-40] U3W40F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W39-40] U3W40F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 11: n_frames=8
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 12: n_frames=8
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W41-42] U11W41F/RightHand trial 8: n_frames=8
- `n_frames_out_of_range` [W41-42] U12W42F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W41-42] U12W42F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W41-42] U12W42F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W41-42] U12W42F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W41-42] U12W42F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W41-42] U13W41F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W41-42] U13W41F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W41-42] U13W42F/RightHand trial 15: n_frames=8
- `n_frames_out_of_range` [W41-42] U13W42F/RightHand trial 16: n_frames=8
- `n_frames_out_of_range` [W41-42] U13W42F/RightHand trial 17: n_frames=8
- `n_frames_out_of_range` [W41-42] U2W41F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W41-42] U2W41F/RightHand trial 13: n_frames=8
- `n_frames_out_of_range` [W41-42] U2W41F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W41-42] U2W41F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W41-42] U3W41F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W41-42] U3W41F/RightHand trial 12: n_frames=8
- `n_frames_out_of_range` [W41-42] U3W41F/RightHand trial 15: n_frames=9
- `n_frames_out_of_range` [W41-42] U3W41F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W41-42] U3W42F/RightHand trial 11: n_frames=8
- `n_frames_out_of_range` [W41-42] U3W42F/RightHand trial 12: n_frames=8
- `n_frames_out_of_range` [W41-42] U3W42F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W41-42] U3W42F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W41-42] U4W41F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W41-42] U6W42F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W43-44] U11W43F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W43-44] U11W43F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W43-44] U11W43F/RightHand trial 13: n_frames=9
- `n_frames_out_of_range` [W43-44] U15W44F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W43-44] U1W43F/LeftHand trial 0: n_frames=8
- `n_frames_out_of_range` [W43-44] U3W43F/RightHand trial 2: n_frames=8
- `n_frames_out_of_range` [W43-44] U3W43F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W45-46] U11W45F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W45-46] U1W46F/LeftHand trial 0: n_frames=8
- `n_frames_out_of_range` [W45-46] U2W45F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W45-46] U2W46F/LeftHand trial 5: n_frames=9
- `n_frames_out_of_range` [W45-46] U3W45F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W45-46] U3W45F/RightHand trial 13: n_frames=8
- `n_frames_out_of_range` [W45-46] U3W45F/RightHand trial 15: n_frames=9
- `n_frames_out_of_range` [W45-46] U3W45F/RightHand trial 16: n_frames=8
- `n_frames_out_of_range` [W45-46] U3W45F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W49-50] U11W50F/RightHand trial 17: n_frames=9
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W49-50] U12W49F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W49-50] U1W50F/LeftHand trial 18: n_frames=9
- `n_frames_out_of_range` [W49-50] U1W50F/LeftHand trial 9: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 11: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 13: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 4: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W49-50] U3W49F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W49-50] U3W50F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W7-8] U15W8F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W9-10] U15W9F/RightHand trial 0: n_frames=9
- `n_frames_out_of_range` [W9-10] U15W9F/RightHand trial 6: n_frames=9
- `n_frames_out_of_range` [W9-10] U15W9F/RightHand trial 7: n_frames=8
- `n_frames_out_of_range` [W9-10] U15W9F/RightHand trial 8: n_frames=9
- `n_frames_out_of_range` [W9-10] U2W10F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W91-92] U15W92F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W91-92] U15W92F/RightHand trial 5: n_frames=8
- `n_frames_out_of_range` [W91-92] U15W92F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W91-92] U15W92F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W91-92] U1W92F/LeftHand trial 12: n_frames=8
- `n_frames_out_of_range` [W91-92] U1W92F/LeftHand trial 13: n_frames=8
- `n_frames_out_of_range` [W91-92] U1W92F/LeftHand trial 3: n_frames=9
- `n_frames_out_of_range` [W91-92] U6W91F/RightHand trial 3: n_frames=9
- `n_frames_out_of_range` [W91-92] U6W92F/RightHand trial 11: n_frames=9
- `n_frames_out_of_range` [W91-92] U6W92F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W91-92] U6W92F/RightHand trial 3: n_frames=8
- `n_frames_out_of_range` [W93-94] U12W94F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W93-94] U1W94F/RightHand trial 10: n_frames=9
- `n_frames_out_of_range` [W93-94] U1W94F/RightHand trial 11: n_frames=8
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 10: n_frames=8
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 2: n_frames=9
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 4: n_frames=8
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 5: n_frames=9
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 6: n_frames=8
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 7: n_frames=9
- `n_frames_out_of_range` [W93-94] U6W93F/RightHand trial 9: n_frames=8
- `n_frames_out_of_range` [W93-94] U6W94F/RightHand trial 1: n_frames=8
- `n_frames_out_of_range` [W97-98] U6W97F/RightHand trial 12: n_frames=9
- `n_frames_out_of_range` [W97-98] U6W97F/RightHand trial 1: n_frames=9
- `n_frames_out_of_range` [W97-98] U6W97F/RightHand trial 9: n_frames=9
- `n_frames_out_of_range` [W97-98] U6W98F/RightHand trial 3: n_frames=8
- `no_of_trials_mismatch` [W1-2] U10W2F/LeftHand: declared 0 != 5
- `no_of_trials_mismatch` [W11-12] U9W11F/RightHand: declared 11 != 10
- `no_of_trials_mismatch` [W111-112] U5W112F/RightHand: declared 11 != 10
- `no_of_trials_mismatch` [W19-20] U12W19F/RightHand: declared 13 != 10
- `no_of_trials_mismatch` [W19-20] U15W19F/RightHand: declared 10 != 9
- `no_of_trials_mismatch` [W19-20] U2W20F/LeftHand: declared 15 != 14
- `no_of_trials_mismatch` [W213-214] U4W214F/LeftHand: declared 11 != 10
- `no_of_trials_mismatch` [W215-216] U11W216F/RightHand: declared 14 != 13
- `no_of_trials_mismatch` [W215-216] U6W215F/RightHand: declared 17 != 18
- `no_of_trials_mismatch` [W215-216] U8W215F/RightHand: declared 11 != 10
- `no_of_trials_mismatch` [W219-220] U11W220F/RightHand: declared 16 != 15
- `no_of_trials_mismatch` [W219-220] U12W219F/RightHand: declared 9 != 10
- `no_of_trials_mismatch` [W219-220] U15W219F/RightHand: declared 10 != 11
- `no_of_trials_mismatch` [W219-220] U4W219F/RightHand: declared 9 != 10
- `no_of_trials_mismatch` [W219-220] U5W219F/RightHand: declared 9 != 10
- `no_of_trials_mismatch` [W219-220] U6W219F/RightHand: declared 20 != 21
- `no_of_trials_mismatch` [W219-220] U8W219F/RightHand: declared 9 != 10
- `no_of_trials_mismatch` [W351-352] U11W351F/RightHand: declared 7 != 8
- `no_of_trials_mismatch` [W351-352] U12W351F/RightHand: declared 10 != 20
- `no_of_trials_mismatch` [W351-352] U18W352F/RightHand: declared 12 != 13
- `no_of_trials_mismatch` [W351-352] U2W351F/RightHand: declared 10 != 12
- `no_of_trials_mismatch` [W351-352] U3W352F/RightHand: declared 14 != 15
- `no_of_trials_mismatch` [W37-38] U10W38F/RightHand: declared 11 != 8
- `no_of_trials_mismatch` [W37-38] U2W38F/LeftHand: declared 5 != 4
- `no_of_trials_mismatch` [W37-38] U3W38F/RightHand: declared 15 != 14
- `no_of_trials_mismatch` [W37-38] U5W38F/RightHand: declared 10 != 9
- `no_of_trials_mismatch` [W37-38] U9W38F/RightHand: declared 11 != 10
- `no_of_trials_mismatch` [W45-46] U10W46F/LeftHand: declared 12 != 11
- `no_of_trials_mismatch` [W49-50] U13W50F/RightHand: declared 9 != 10
- `no_of_trials_mismatch` [W5-6] U13W5F/LeftHand: declared 18 != 17
- `no_of_trials_mismatch` [W7-8] U3W8F/RightHand: declared 19 != 20
- `no_of_trials_mismatch` [W7-8] U4W8F/LeftHand: declared 10 != 11
- `no_of_trials_mismatch` [W7-8] U9W7F/RightHand: declared 11 != 12
- `no_of_trials_mismatch` [W91-92] U15W91F/RightHand: declared 8 != 11
- `no_of_trials_mismatch` [W93-94] U5W94F/RightHand: declared 9 != 8
- `no_of_trials_mismatch` [W97-98] U13W98F/LeftHand: declared 11 != 10
- `no_of_trials_mismatch` [W99-100] U13W99F/RightHand: declared 4 != 9
- `no_of_trials_unparsable` [W111-112] U2W112F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W111-112] U4W112F/RightHand: no_of_trials='' (have 12)
- `no_of_trials_unparsable` [W111-112] U9W111F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W111-112] U9W112F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W211-212] U2W211F/RightHand: no_of_trials='' (have 15)
- `no_of_trials_unparsable` [W211-212] U2W212F/LeftHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W211-212] U9W211F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W211-212] U9W212F/RightHand: no_of_trials='*/' (have 12)
- `no_of_trials_unparsable` [W213-214] U2W213F/RightHand: no_of_trials='' (have 18)
- `no_of_trials_unparsable` [W213-214] U2W214F/RightHand: no_of_trials='*/' (have 14)
- `no_of_trials_unparsable` [W213-214] U9W213F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W213-214] U9W214F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W215-216] U15W216F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W215-216] U2W215F/RightHand: no_of_trials='' (have 13)
- `no_of_trials_unparsable` [W215-216] U2W216F/RightHand: no_of_trials='*/' (have 14)
- `no_of_trials_unparsable` [W215-216] U9W215F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W215-216] U9W216F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W217-218] U2W217F/LeftHand: no_of_trials='' (have 5)
- `no_of_trials_unparsable` [W217-218] U2W218F/RightHand: no_of_trials='*/' (have 15)
- `no_of_trials_unparsable` [W217-218] U9W217F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W217-218] U9W218F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W219-220] U11W219F/LeftHand: no_of_trials='' (have 8)
- `no_of_trials_unparsable` [W219-220] U1W220F/RightHand: no_of_trials='' (have 16)
- `no_of_trials_unparsable` [W219-220] U2W219F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W219-220] U2W220F/RightHand: no_of_trials='*/' (have 19)
- `no_of_trials_unparsable` [W219-220] U9W219F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W219-220] U9W220F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W351-352] U15W352F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W351-352] U9W351F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W351-352] U9W352F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W353-354] U9W353F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W353-354] U9W354F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W355-356] U1W355F/LeftHand: no_of_trials='*/' (have 16)
- `no_of_trials_unparsable` [W355-356] U9W355F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W355-356] U9W356F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W357-358] U9W357F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W357-358] U9W358F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W359-360] U16W359F/RightHand: no_of_trials='' (have 5)
- `no_of_trials_unparsable` [W359-360] U9W359F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W359-360] U9W360F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W37-38] U13W38F/RightHand: no_of_trials='' (have 6)
- `no_of_trials_unparsable` [W37-38] U15W38F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W39-40] U8W40F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U10W41F/LeftHand: no_of_trials='' (have 13)
- `no_of_trials_unparsable` [W41-42] U10W42F/LeftHand: no_of_trials='' (have 15)
- `no_of_trials_unparsable` [W41-42] U11W41F/RightHand: no_of_trials='' (have 14)
- `no_of_trials_unparsable` [W41-42] U11W42F/RightHand: no_of_trials='' (have 15)
- `no_of_trials_unparsable` [W41-42] U12W41F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U12W42F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U13W41F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U13W42F/RightHand: no_of_trials='' (have 18)
- `no_of_trials_unparsable` [W41-42] U15W41F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U15W42F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U1W41F/LeftHand: no_of_trials='' (have 20)
- `no_of_trials_unparsable` [W41-42] U1W42F/LeftHand: no_of_trials='' (have 13)
- `no_of_trials_unparsable` [W41-42] U2W41F/RightHand: no_of_trials='' (have 14)
- `no_of_trials_unparsable` [W41-42] U2W42F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W41-42] U3W41F/RightHand: no_of_trials='' (have 19)
- `no_of_trials_unparsable` [W41-42] U3W42F/RightHand: no_of_trials='' (have 14)
- `no_of_trials_unparsable` [W41-42] U4W41F/RightHand: no_of_trials='' (have 8)
- `no_of_trials_unparsable` [W41-42] U4W42F/RightHand: no_of_trials='' (have 12)
- `no_of_trials_unparsable` [W41-42] U5W41F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W41-42] U5W42F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W41-42] U6W41F/RightHand: no_of_trials='' (have 15)
- `no_of_trials_unparsable` [W41-42] U6W42F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W41-42] U8W41F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U8W42F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U9W41F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W41-42] U9W42F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W43-44] U2W44F/RightHand: no_of_trials='' (have 14)
- `no_of_trials_unparsable` [W43-44] U5W43F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W49-50] U2W50F/RightHand: no_of_trials='' (have 0)
- `no_of_trials_unparsable` [W91-92] U1W91F/LeftHand: no_of_trials='' (have 16)
- `no_of_trials_unparsable` [W91-92] U2W91F/RightHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W91-92] U2W92F/RightHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W91-92] U9W91F/LeftHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W91-92] U9W92F/RightHand: no_of_trials='*/' (have 9)
- `no_of_trials_unparsable` [W93-94] U2W93F/RightHand: no_of_trials='' (have 13)
- `no_of_trials_unparsable` [W93-94] U2W94F/RightHand: no_of_trials='*/' (have 12)
- `no_of_trials_unparsable` [W93-94] U9W93F/RightHand: no_of_trials='*/' (have 9)
- `no_of_trials_unparsable` [W93-94] U9W94F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W95-96] U2W95F/RightHand: no_of_trials='' (have 10)
- `no_of_trials_unparsable` [W95-96] U2W96F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W95-96] U9W95F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W95-96] U9W96F/RightHand: no_of_trials='*/' (have 13)
- `no_of_trials_unparsable` [W97-98] U2W97F/LeftHand: no_of_trials='' (have 11)
- `no_of_trials_unparsable` [W97-98] U2W98F/LeftHand: no_of_trials='*/' (have 11)
- `no_of_trials_unparsable` [W97-98] U9W97F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W97-98] U9W98F/RightHand: no_of_trials='*/' (have 10)
- `no_of_trials_unparsable` [W99-100] U2W100F/RightHand: no_of_trials='*/' (have 9)
- `no_of_trials_unparsable` [W99-100] U2W99F/RightHand: no_of_trials='' (have 13)
- `no_of_trials_unparsable` [W99-100] U9W100F/RightHand: no_of_trials='*/' (have 12)
- `no_of_trials_unparsable` [W99-100] U9W99F/RightHand: no_of_trials='*/' (have 13)

</details>
