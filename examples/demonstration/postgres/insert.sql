DELETE FROM public."B";

DELETE FROM public."C";

INSERT INTO public."B" (c, d) VALUES (:id, :c); INSERT INTO public."C" (e, f) VALUES (:id, :d);
