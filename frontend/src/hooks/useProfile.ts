import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchProfiles,
  createProfile,
  deleteProfile,
  activateProfile,
  updateProfile,
} from "@/lib/api";
import type { Profile } from "@/types/fertility";

export function useProfiles() {
  return useQuery<Profile[]>({
    queryKey: ["profiles"],
    queryFn: fetchProfiles,
  });
}

export function useActiveProfile() {
  const { data: profiles, ...rest } = useProfiles();
  const active = profiles?.find((p) => p.is_active) ?? null;
  return { activeProfile: active, profiles, ...rest };
}

export function useCreateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
  });
}

export function useDeleteProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
  });
}

export function useActivateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: activateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      profileId,
      data,
    }: {
      profileId: string;
      data: { name?: string; temp_unit?: string; interpretation_method?: string };
    }) => updateProfile(profileId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profiles"] });
    },
  });
}
