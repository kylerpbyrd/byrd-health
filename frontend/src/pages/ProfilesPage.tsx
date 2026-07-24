import { useState } from "react";
import { useProfiles, useCreateProfile, useDeleteProfile, useActivateProfile } from "@/hooks/useProfile";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2, Trash2, CheckCircle } from "lucide-react";

export default function ProfilesPage() {
  const { data: profiles, isLoading, isError } = useProfiles();
  const createProfile = useCreateProfile();
  const deleteProfile = useDeleteProfile();
  const activateProfile = useActivateProfile();

  const [name, setName] = useState("");

  const handleCreate = () => {
    if (!name.trim()) return;
    createProfile.mutate({ name: name.trim() }, {
      onSuccess: () => setName(""),
    });
  };

  return (
    <div>
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Create Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <div className="flex-1 space-y-1">
              <Label htmlFor="profile-name">Profile Name</Label>
              <Input
                id="profile-name"
                placeholder="e.g. Default Profile"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              />
            </div>
            <Button
              onClick={handleCreate}
              className="mt-auto"
              disabled={createProfile.isPending || !name.trim()}
            >
              {createProfile.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Create"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Profiles</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          )}

          {isError && (
            <p className="py-8 text-center text-muted-foreground">
              Unable to load profiles.
            </p>
          )}

          {!isLoading && !isError && profiles && (
            <div className="divide-y">
              {profiles.map((profile) => (
                <div
                  key={profile.id}
                  className="flex items-center justify-between py-3"
                >
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="font-medium">{profile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {profile.temp_unit} / {profile.interpretation_method === "standard" ? "Standard" : "Conservative"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {profile.is_active ? (
                      <Badge variant="default">Active</Badge>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => activateProfile.mutate(profile.id)}
                        disabled={activateProfile.isPending}
                      >
                        <CheckCircle className="mr-1 h-3 w-3" />
                        Activate
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteProfile.mutate(profile.id)}
                      disabled={deleteProfile.isPending}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
