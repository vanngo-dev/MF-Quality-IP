import { apiGet } from "./apiClient";

export type Equipment = {
  id: number;
  station_id: number;
  asset_tag: string;
  name: string;
  equipment_type: string;
};

export function listEquipment() {
  return apiGet<Equipment[]>("/api/v1/equipment");
}
