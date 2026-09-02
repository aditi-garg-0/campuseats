| Method | URL | Does | Success | Failure |
|--------|-----|------|---------|---------|
| POST | `/orders` | Place a new order | `201` | `400`, `422`, `503` |
| GET | `/orders/{id}` | Read a single order | `200` | `404` |
| GET | `/orders?student={id}` | List a student's orders | `200` | `400` |
| POST | `/orders/{id}/cancel` | Cancel an order | `202` | `404`, `409` |
