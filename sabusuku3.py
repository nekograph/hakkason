import tkinter as tk
from tkinter import messagebox, filedialog
import webbrowser
import json
from datetime import datetime
from PIL import Image, ImageTk
import os

class SubscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSM")
        self.subscriptions = []
        self.load_subscriptions_from_file()
        self.show_home_screen()


    def load_subscriptions_from_file(self):
        try:
            with open('subscriptions.json', 'r', encoding='utf-8') as file:
                self.subscriptions = json.load(file)
        except FileNotFoundError:
            self.subscriptions = []


    def save_subscriptions_to_file(self):
        with open('subscriptions.json', 'w', encoding='utf-8') as file:
            json.dump(self.subscriptions, file, ensure_ascii=False, indent=4)


    def show_home_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="SSM(サブスクマトメル)", font=("Arial", 20)).pack(pady=20)
        total_price = sum(int(sub['price']) for sub in self.subscriptions)
        tk.Label(self.root, text=f"合計金額: {total_price} 円", font=("Arial", 14)).pack(pady=10)
        

        sort_options = ["値段の高い順", "値段の低い順", "登録の新しい順", "登録の古い順"]
        self.sort_var = tk.StringVar(self.root)

        self.sort_var.set("並べ替え")  # 初期値を設定

        sort_menu = tk.OptionMenu(self.root, self.sort_var, *sort_options, command=self.on_sort_change)
        sort_menu.config(font=("Arial", 12))
        sort_menu.pack(pady=10)
    
        #FrameとCanvasの設定
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        for i in range(5):
            scrollable_frame.grid_columnconfigure(i, weight=1)

        # 中央揃えのためのスペーサー
        tk.Label(scrollable_frame).grid(row=0, column=0,sticky='w,e')
        tk.Label(scrollable_frame).grid(row=0, column=4)

        #サブスク名と金額のラベルをグリッド形式で表示
        tk.Label(scrollable_frame, text="アイコン", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=2,sticky='n')
        tk.Label(scrollable_frame, text="サブスク名", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=2,sticky='n')
        tk.Label(scrollable_frame, text="金額", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=10, pady=2,sticky='n')

        #サブスク名と金額と画像ラベルをグリッド形式で表示
        for idx, sub in enumerate(self.subscriptions):
            if 'image_path' in sub and sub['image_path']:
                try:
                    image = Image.open(sub['image_path'])
                    image = image.resize((50, 50), resample=Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(scrollable_frame, image=photo)
                    image_label.image = photo
                    image_label.grid(row=idx+1, column=1, padx=5, pady=2, sticky="e")
                except Exception as e:
                    print(f"Error loading image: {e}")
                    tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 12)).grid(row=idx+1, column=1, padx=5, pady=2, sticky="e")
            else:
                tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 6)).grid(row=idx+1, column=1, padx=5, pady=2, sticky="e")
            name_label = tk.Label(scrollable_frame, text=sub['name'], font=("Arial", 12), fg="blue", cursor="hand2")
            name_label.grid(row=idx+1, column=2, padx=5, pady=2, sticky="e")
            name_label.bind("<Button-1>", lambda e, index=idx: self.show_subscription_details(index))

            price_label = tk.Label(scrollable_frame, text=f"{sub['price']} 円", font=("Arial", 12))
            price_label.grid(row=idx+1, column=3, padx=5, pady=2, sticky="e")

        #サブスクリプションの一覧を表示
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        #新規入力ボタン
        tk.Button(self.root, text="新規入力", command=self.show_new_entry_screen, bg="gray", width=10, height=3).pack(pady=20)

        #検索ボタン
        tk.Button(self.root, text="名前検索", command=self.show_search_screen_name).pack(pady=20)
        tk.Button(self.root, text="値段検索", command=self.show_search_screen_price).pack(pady=5)


    def on_sort_change(self, event):
        self.sort_subscriptions()
        self.show_home_screen()

    def sort_subscriptions(self):
        select_s = self.sort_var.get()
        if select_s == "値段の高い順":
            self.subscriptions.sort(key=lambda x: int(x['price']), reverse=True)
        elif select_s == "値段の低い順":
            self.subscriptions.sort(key=lambda x: int(x['price']))
        elif select_s == "登録の新しい順":
            self.subscriptions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        elif select_s == "登録の古い順":
            self.subscriptions.sort(key=lambda x: x.get('timestamp', ''))


    def show_new_entry_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="新規サブスク登録", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text="サブスク名:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="値段:").pack()
        self.price_entry = tk.Entry(self.root)
        self.price_entry.pack()

        tk.Label(self.root, text="URL:").pack()
        self.url_entry = tk.Entry(self.root)
        self.url_entry.pack()

        tk.Label(self.root, text="その他情報:").pack()
        self.info_entry = tk.Entry(self.root)
        self.info_entry.pack()

        tk.Button(self.root, text="画像を選択", command=self.choose_image).pack(pady=10)
        tk.Button(self.root, text="登録", command=self.save_subscription,bg="green" ).pack(pady=20)
        tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)


    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            self.image_path = file_path


    def save_subscription(self):
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        url = self.url_entry.get().strip()
        info = self.info_entry.get().strip()
        if not name:
            messagebox.showerror("エラー", "サブスク名は必須です。")
            return
        try:
            price = int(price)
            new_subscription = {
                'name': name,
                'price': price,
                'url': url,
                'info': info,
                'image_path': self.image_path if hasattr(self, 'image_path') else None,
                'timestamp': datetime.now().isoformat()
            }
            self.subscriptions.append(new_subscription)
            self.save_subscriptions_to_file()
            messagebox.showinfo("成功", "サブスクが登録されました！")
            self.show_home_screen()
        except ValueError:
            messagebox.showerror("エラー", "値段は整数で入力してください。")


    def show_subscription_details(self, index):
        self.clear_screen()
        subscription = self.subscriptions[index]
        tk.Label(self.root, text=f"サブスク名: {subscription['name']}", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text=f"値段: {subscription['price']} 円", font=("Arial", 14)).pack(pady=10)
        
        url_label = tk.Label(self.root, text=f"URL: {subscription['url']}", font=("Arial", 14), fg="blue", cursor="hand2")
        url_label.pack(pady=10)
        url_label.bind("<Button-1>", lambda e, url=subscription['url']: self.open_url(url))
        
        if 'image_path' in subscription and subscription['image_path']:
            try:
                image = Image.open(subscription['image_path'])
                image = image.resize((100, 100), resample=Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = tk.Label(self.root, image=photo)
                image_label.image = photo
                image_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading image: {e}")

        tk.Label(self.root, text=f"その他情報: {subscription['info']}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="サブスク名編集", command=lambda: self.edit_subscription_detail(index, 'name')).pack(pady=5)
        tk.Button(self.root, text="値段編集", command=lambda: self.edit_subscription_detail_val(index, 'price')).pack(pady=5)
        tk.Button(self.root, text="URL編集", command=lambda: self.edit_subscription_detail(index, 'url')).pack(pady=5)
        tk.Button(self.root, text="その他情報編集", command=lambda: self.edit_subscription_detail(index, 'info')).pack(pady=5)
        tk.Button(self.root, text="アイコン変更", command=lambda: self.change_subscription_image(index)).pack(pady=5)
        tk.Button(self.root, text="アイコン削除", command=lambda: self.delete_subscription_image(index)).pack(pady=5)
        tk.Button(self.root, text="削除", command=lambda: self.confirm_delete_subscription(index), bg="red", fg="white").pack(pady=20)
        tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)


    def edit_subscription_detail(self, index, detail_type):
        current_value = self.subscriptions[index][detail_type]
        self.clear_screen()
        tk.Label(self.root, text=f"編集: {detail_type}", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text=f"現在の値: {current_value}", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="新しい値を入力してください:").pack()

        new_value_entry = tk.Entry(self.root)
        new_value_entry.pack()
        tk.Button(self.root, text="更新", command=lambda: self.update_subscription_detail(index, detail_type, new_value_entry.get()),bg="green").pack(pady=20)
        tk.Button(self.root, text="キャンセル", command=lambda: self.show_subscription_details(index), bg="red", fg="white").pack(pady=10)

    def edit_subscription_detail_val(self, index, detail_type):
        current_value = self.subscriptions[index][detail_type]
        self.clear_screen()
        tk.Label(self.root, text=f"編集: {detail_type}", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text=f"現在の値: {current_value}", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="新しい値を入力してください:").pack()
        
        new_value_entry = tk.Entry(self.root)
        new_value_entry.pack()
        
        tk.Button(self.root, text="更新", command=lambda: self.update_subscription_detail_val(index, detail_type, new_value_entry.get()), bg="green").pack(pady=20)
        tk.Button(self.root, text="キャンセル", command=lambda: self.show_subscription_details(index), bg="red", fg="white").pack(pady=10)


    def change_subscription_image(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            self.subscriptions[index]['image_path'] = file_path
            self.save_subscriptions_to_file()
            messagebox.showinfo("成功", "アイコン画像が変更されました！")
            self.show_subscription_details(index)

    def delete_subscription_image(self, index):
        if 'image_path' in self.subscriptions[index]:
            try:
                # アイコンファイルが存在する場合は削除する
                if os.path.exists(self.subscriptions[index]['image_path']):
                    os.remove(self.subscriptions[index]['image_path'])
                    messagebox.showinfo("成功", "アイコン画像が削除されました！")
                else:
                    messagebox.showinfo("情報", "削除するアイコン画像が見つかりませんでした。")
                # サブスクリプション情報から画像パスを削除
                del self.subscriptions[index]['image_path']
                self.save_subscriptions_to_file()
                self.show_subscription_details(index)
            except Exception as e:
                messagebox.showerror("エラー", f"アイコン画像の削除中にエラーが発生しました: {e}")


    def update_subscription_detail(self, index, detail_type, new_value):
        self.subscriptions[index][detail_type] = new_value
        self.save_subscriptions_to_file()
        messagebox.showinfo("成功", f"{detail_type} が更新されました！")
        self.show_home_screen()

    def update_subscription_detail_val(self, index, detail_type, new_value):
        try:
            new_value= int(new_value)
            self.subscriptions[index][detail_type] = new_value
            self.save_subscriptions_to_file()  # サブスクリプションをファイルに保存
            messagebox.showinfo("成功", f"{detail_type} が更新されました！")
            self.show_home_screen()
        except ValueError:
            messagebox.showerror("エラー", "値段は整数で入力してください。")


    def confirm_delete_subscription(self, index):
        if messagebox.askyesno("確認", "本当に削除していいですか？"):
            self.delete_subscription(index)


    def delete_subscription(self, index):
        del self.subscriptions[index]
        self.save_subscriptions_to_file()
        messagebox.showinfo("成功", "サブスクが削除されました！")
        self.show_home_screen()


    def open_url(self, url):
        webbrowser.open_new(url)


    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    

    def show_search_screen_name(self):
        self.clear_screen()
        tk.Label(self.root, text="商品名を入力してください").pack(pady=10)

        self.search_entry_name = tk.Entry(self.root)
        self.search_entry_name.pack(pady=20)

        tk.Button(self.root, text="検索", command=self.search_name).pack()
        tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)

    def search_name(self):
        name = self.search_entry_name.get().strip()
        self.clear_screen()

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        for idx, sub in enumerate(self.subscriptions):
            if name.lower() in sub['name'].lower():
                if 'image_path' in sub and sub['image_path']:
                    try:
                        image = Image.open(sub['image_path'])
                        image = image.resize((50, 50), resample=Image.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        image_label = tk.Label(scrollable_frame, image=photo)
                        image_label.image = photo
                        image_label.grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                    except Exception as e:
                        print(f"Error loading image: {e}")
                        tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 12)).grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                else:
                    tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 6)).grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                name_label = tk.Label(scrollable_frame, text=sub['name'], font=("Arial", 12), fg="blue", cursor="hand2")
                name_label.grid(row=idx+1, column=1, padx=5, pady=2, sticky="e")
                name_label.bind("<Button-1>", lambda e, index=idx: self.show_subscription_details(index))

                price_label = tk.Label(scrollable_frame, text=f"{sub['price']} 円", font=("Arial", 12))
                price_label.grid(row=idx+1, column=2, padx=5, pady=2, sticky="e")

        tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)
    

    def show_search_screen_price(self):
        self.clear_screen()
        tk.Label(self.root, text="値段を入力してください").pack(pady=10)

        search_entry_price_low = tk.Entry(self.root)
        search_entry_price_low.pack(pady=10)
        tk.Label(self.root, text="以上").pack()
        
        search_entry_price_high = tk.Entry(self.root)
        search_entry_price_high.pack(pady=10)
        tk.Label(self.root, text="以下").pack()


        tk.Button(self.root, text="検索", command=lambda:self.search_price(search_entry_price_low.get(), search_entry_price_high.get())).pack(pady=10)
        tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)

    def search_price(self,low_price,high_price):
        self.clear_screen()

        try:
            low_price = int(low_price)
            high_price =  int(high_price)
            frame = tk.Frame(self.root)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)
        
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            for idx, sub in enumerate(self.subscriptions):
                if low_price<=int(sub['price']) and high_price>=int(sub['price']):
                    if 'image_path' in sub and sub['image_path']:
                        try:
                            image = Image.open(sub['image_path'])
                            image = image.resize((50, 50), resample=Image.LANCZOS)
                            photo = ImageTk.PhotoImage(image)
                            image_label = tk.Label(scrollable_frame, image=photo)
                            image_label.image = photo
                            image_label.grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                        except Exception as e:
                            print(f"Error loading image: {e}")
                            tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 12)).grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                    else:
                        tk.Label(scrollable_frame, text="アイコンなし", font=("Arial", 6)).grid(row=idx+1, column=0, padx=5, pady=2, sticky="e")
                    name_label = tk.Label(scrollable_frame, text=sub['name'], font=("Arial", 12), fg="blue", cursor="hand2")
                    name_label.grid(row=idx+1, column=1, padx=5, pady=2, sticky="e")
                    name_label.bind("<Button-1>", lambda e, index=idx: self.show_subscription_details(index))

                    price_label = tk.Label(scrollable_frame, text=f"{sub['price']} 円", font=("Arial", 12))
                    price_label.grid(row=idx+1, column=2, padx=5, pady=2, sticky="e")

            tk.Button(self.root, text="ホームに戻る", command=self.show_home_screen).pack(pady=10)

        except ValueError:
            messagebox.showerror("エラー", "値段は整数で入力してください。")
            self.show_search_screen_price()


if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriptionApp(root)
    root.mainloop()