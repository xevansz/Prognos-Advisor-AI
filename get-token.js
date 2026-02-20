import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  "https://faqdcwuuondgwkceoylh.supabase.co",
  "sb_publishable_bqT3ltdVEBzbTfdwlHOxLQ_KS4vy55Z",
);

// const { data, error } = await supabase.auth.signUp({
//   email: 'newuser@example.com',
//   password: 'your-secure-password'
// })

const { data, error } = await supabase.auth.signInWithPassword({
  email: "test@test.com",
  password: "test@test",
});

if (error) {
  console.error("Error:", error.message);
} else {
  console.log("JWT Token:");
  console.log(data.session.access_token);
}
