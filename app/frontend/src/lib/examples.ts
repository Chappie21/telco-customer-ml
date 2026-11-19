import type { Customer } from "@/types/customer";

export const EXAMPLES: { id: string; label: string; customer: Customer }[] = [
  {
    id: "new-fiber",
    label: "Cliente nuevo con fibra",
    customer: {
      senior_citizen: false, partner: false, dependents: false, tenure: 3,
      phone_service: true, multiple_lines: false, internet_service: "fiber_optic",
      online_security: false, online_backup: false, device_protection: false, tech_support: false,
      streaming_tv: true, streaming_movies: false, contract: "month_to_month",
      paperless_billing: true, payment_method: "electronic_check",
      monthly_charges: 85.5, total_charges: 256.5,
    },
  },
  {
    id: "loyal",
    label: "Cliente de 5 años, contrato 2 años",
    customer: {
      senior_citizen: false, partner: true, dependents: true, tenure: 60,
      phone_service: true, multiple_lines: false, internet_service: "dsl",
      online_security: true, online_backup: true, device_protection: true, tech_support: true,
      streaming_tv: false, streaming_movies: false, contract: "two_year",
      paperless_billing: false, payment_method: "credit_card_automatic",
      monthly_charges: 60, total_charges: 3600,
    },
  },
];
