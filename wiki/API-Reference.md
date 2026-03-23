# API Reference

## `POST /compare`

Compares Blue and Red compositions and returns scoring + breakdown data.

### Request Body

```json
{
  "blue": ["Aatrox", "Vi", "Syndra", "Kai'Sa", "Nautilus"],
  "red": ["K'Sante", "Sejuani", "Taliyah", "Xayah", "Rakan"]
}
```

### Response Shape (example)

```json
{
  "score": 49.04,
  "blue": {
    "wincon": ["front_to_back"],
    "synergy": 5.6,
    "comfort": 0,
    "counter": 0.15,
    "summary": "..."
  },
  "red": {
    "wincon": ["front_to_back"],
    "synergy": 5.61,
    "comfort": 0,
    "counter": 0.06,
    "summary": "..."
  }
}
```
