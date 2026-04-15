// Convex query functions for content pipeline
import { query } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("content_items").collect();
  },
});

export const getByStatus = query({
  args: { status: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("content_items")
      .withIndex("by_status", (q) => q.eq("production_status", args.status))
      .collect();
  },
});